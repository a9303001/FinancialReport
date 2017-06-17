"""Work around the Claude Code cloud egress proxy rejecting curl_cffi's Chrome TLS fingerprint.

yfinance calls curl_cffi with impersonate="chrome". The cloud session's egress
proxy re-terminates TLS and resets connections carrying Chrome's (or Firefox's)
ClientHello, so every yfinance request dies with
"curl: (35) Recv failure: Connection reset by peer". Safari's fingerprint is
accepted, so force that instead.

Python imports this automatically at interpreter startup when its directory is
on PYTHONPATH. It is a no-op outside the cloud sandbox, so local runs keep
yfinance's stock behaviour.
"""
import os

if os.environ.get("CCR_AGENT_PROXY_ENABLED") == "1":
    try:
        from curl_cffi import requests as _curl_requests

        def _pin_safari(cls):
            original_init = cls.__init__

            def __init__(self, *args, **kwargs):
                kwargs["impersonate"] = "safari"
                return original_init(self, *args, **kwargs)

            cls.__init__ = __init__

        _pin_safari(_curl_requests.Session)
        _pin_safari(_curl_requests.AsyncSession)
    except Exception:
        # Never break interpreter startup for a best-effort workaround.
        pass
