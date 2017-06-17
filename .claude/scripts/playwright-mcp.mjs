#!/usr/bin/env node
// Cross-platform launcher for @playwright/mcp.
//
// Exists because a static mcp config cannot satisfy both environments:
//   - Claude Code on the cloud: Linux container, runs as root, no display, only
//     Playwright's bundled Chromium (no Google Chrome), and outbound HTTPS is
//     re-terminated by an agent proxy whose CA Chromium does not trust.
//   - Google Antigravity on the local machine: Windows/macOS with real Chrome,
//     a display, and no proxy.
//
// The launcher resolves a browser executable, decides headless/sandbox/CA flags
// for the current machine, writes a temporary @playwright/mcp config, and execs
// the server. stdout is reserved for JSON-RPC: diagnostics go to stderr only.
//
// Env overrides: PLAYWRIGHT_MCP_EXECUTABLE, PLAYWRIGHT_MCP_HEADLESS (0|1),
// PLAYWRIGHT_MCP_VERSION, PLAYWRIGHT_MCP_CA_CERT, PLAYWRIGHT_MCP_DEBUG.

import { spawn } from 'node:child_process';
import { createHash, X509Certificate } from 'node:crypto';
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const MCP_VERSION = process.env.PLAYWRIGHT_MCP_VERSION || '0.0.82';
const log = (msg) => process.stderr.write(`[playwright-mcp-launcher] ${msg}\n`);

// Expand a single `chromium-*` style wildcard segment against the filesystem.
function expandGlob(pattern) {
  const star = pattern.indexOf('*');
  if (star === -1) return existsSync(pattern) ? [pattern] : [];
  const dir = path.dirname(pattern.slice(0, star));
  const segment = path.basename(pattern.slice(0, star + 1));
  const rest = pattern.slice(dir.length + 1 + segment.length);
  const prefix = segment.slice(0, -1);
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return [];
  }
  return entries
    .filter((name) => name.startsWith(prefix))
    .sort()
    .reverse() // newest build number first
    .map((name) => path.join(dir, name + rest))
    .filter((candidate) => existsSync(candidate));
}

function browserCandidates() {
  const env = process.env;
  const home = env.HOME || env.USERPROFILE || '';
  const pwPath = env.PLAYWRIGHT_BROWSERS_PATH;

  if (process.platform === 'win32') {
    const roots = [env.ProgramFiles, env['ProgramFiles(x86)'], env.LOCALAPPDATA].filter(Boolean);
    return [
      ...roots.map((r) => path.join(r, 'Google', 'Chrome', 'Application', 'chrome.exe')),
      ...(pwPath ? [path.join(pwPath, 'chromium-*', 'chrome-win', 'chrome.exe')] : []),
      path.join(env.LOCALAPPDATA || '', 'ms-playwright', 'chromium-*', 'chrome-win', 'chrome.exe'),
      ...roots.map((r) => path.join(r, 'Microsoft', 'Edge', 'Application', 'msedge.exe')),
    ];
  }

  if (process.platform === 'darwin') {
    return [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      ...(pwPath ? [path.join(pwPath, 'chromium-*', 'chrome-mac', 'Chromium.app', 'Contents', 'MacOS', 'Chromium')] : []),
      path.join(home, 'Library', 'Caches', 'ms-playwright', 'chromium-*', 'chrome-mac', 'Chromium.app', 'Contents', 'MacOS', 'Chromium'),
    ];
  }

  return [
    // Cloud image ships this symlink; prefer it over any build-numbered dir.
    ...(pwPath ? [path.join(pwPath, 'chromium'), path.join(pwPath, 'chromium-*', 'chrome-linux', 'chrome')] : []),
    '/opt/pw-browsers/chromium',
    '/opt/pw-browsers/chromium-*/chrome-linux/chrome',
    path.join(home, '.cache', 'ms-playwright', 'chromium-*', 'chrome-linux', 'chrome'),
    '/opt/google/chrome/chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
  ];
}

function resolveExecutable() {
  const override = process.env.PLAYWRIGHT_MCP_EXECUTABLE;
  if (override) {
    if (existsSync(override)) return override;
    log(`WARN PLAYWRIGHT_MCP_EXECUTABLE not found: ${override}`);
  }
  for (const candidate of browserCandidates()) {
    const [found] = expandGlob(candidate);
    if (found) return found;
  }
  return null;
}

// Chromium has no CA-file flag, so trust the proxy CA by pinning its public key
// hash. This is scoped to one locally verified certificate and is NOT the same
// as --ignore-certificate-errors, which would disable verification entirely.
function proxyCaSpki() {
  const candidates = [
    process.env.PLAYWRIGHT_MCP_CA_CERT,
    '/root/.ccr/agent-proxy-ca.crt',
    process.env.NODE_EXTRA_CA_CERTS,
  ].filter(Boolean);

  for (const file of candidates) {
    if (!existsSync(file)) continue;
    try {
      const pems = readFileSync(file, 'utf8').match(/-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----/g);
      // A proxy CA file holds one cert or a short chain; a system bundle holds
      // hundreds and must not be pinned wholesale.
      if (!pems || pems.length > 5) continue;
      const hashes = pems.map((pem) => {
        const der = new X509Certificate(pem).publicKey.export({ type: 'spki', format: 'der' });
        return createHash('sha256').update(der).digest('base64');
      });
      return { hash: hashes.join(','), file };
    } catch (err) {
      log(`WARN could not read CA ${file}: ${err.message}`);
    }
  }
  return null;
}

function wantsHeadless() {
  const override = process.env.PLAYWRIGHT_MCP_HEADLESS;
  if (override === '1' || override === 'true') return true;
  if (override === '0' || override === 'false') return false;
  // A headed browser survives bot checks better, so only force headless where
  // no display exists (the cloud container).
  return process.platform === 'linux' && !process.env.DISPLAY && !process.env.WAYLAND_DISPLAY;
}

const executablePath = resolveExecutable();
const headless = wantsHeadless();
const isRoot = process.platform !== 'win32' && typeof process.getuid === 'function' && process.getuid() === 0;

const chromiumArgs = [];
if (isRoot) chromiumArgs.push('--no-sandbox'); // Chromium refuses to sandbox as root
const ca = proxyCaSpki();
if (ca) chromiumArgs.push(`--ignore-certificate-errors-spki-list=${ca.hash}`);

const launchOptions = { headless, args: chromiumArgs };
if (executablePath) launchOptions.executablePath = executablePath;

const configDir = mkdtempSync(path.join(tmpdir(), 'pw-mcp-'));
const configPath = path.join(configDir, 'config.json');
writeFileSync(configPath, JSON.stringify({ browser: { browserName: 'chromium', launchOptions } }, null, 2));

if (executablePath) {
  log(`browser: ${executablePath}`);
} else {
  log('browser: none detected, falling back to the Playwright-managed download');
}
log(`headless=${headless} no-sandbox=${isRoot} proxy-ca=${ca ? ca.file : 'none'}`);
if (process.env.PLAYWRIGHT_MCP_DEBUG) log(`config: ${readFileSync(configPath, 'utf8')}`);

const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const child = spawn(
  npx,
  ['-y', `@playwright/mcp@${MCP_VERSION}`, '--config', configPath, ...process.argv.slice(2)],
  { stdio: 'inherit', env: process.env },
);

const cleanup = () => rmSync(configDir, { recursive: true, force: true });
child.on('error', (err) => {
  log(`failed to start @playwright/mcp: ${err.message}`);
  cleanup();
  process.exit(1);
});
child.on('exit', (code, signal) => {
  cleanup();
  process.exit(signal ? 1 : code ?? 0);
});
for (const sig of ['SIGINT', 'SIGTERM']) process.on(sig, () => child.kill(sig));
