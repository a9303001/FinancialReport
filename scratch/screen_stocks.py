import yfinance as yf
import random

tw_tickers = ['2301.TW', '2377.TW', '3231.TW', '2353.TW', '2357.TW', '3044.TW', '2884.TW', '2886.TW', '1101.TW', '1301.TW', '2385.TW', '2324.TW', '2356.TW', '3037.TW', '2313.TW', '2892.TW', '2880.TW', '2303.TW', '2345.TW', '1504.TW']
us_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'BRK-B', 'JNJ', 'V', 'PG', 'NVDA', 'JPM', 'UNH', 'HD', 'MA', 'BAC', 'DIS', 'CVX', 'PEP', 'KO', 'MRK', 'PFE', 'INTC', 'CMCSA', 'CSCO', 'ABT', 'VZ', 'CRM', 'T', 'WMT', 'F', 'GM', 'WBA']
hk_tickers = ['0700.HK', '0941.HK', '0939.HK', '1398.HK', '3988.HK', '0386.HK', '0005.HK', '0883.HK', '0857.HK', '0001.HK', '0016.HK', '0002.HK', '0823.HK', '0003.HK', '0011.HK', '0388.HK', '0027.HK', '0066.HK', '1113.HK', '1928.HK']
jp_tickers = ['7203.T', '6758.T', '9984.T', '9432.T', '8035.T', '6861.T', '7974.T', '6098.T', '8306.T', '4063.T', '4568.T', '8058.T', '8766.T', '8031.T', '6902.T', '6981.T', '9433.T', '6301.T', '7751.T', '7267.T', '5401.T', '1605.T']

def check_stock(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info:
            return False, "No info"
            
        pe = info.get('trailingPE')
        if pe is None or not (5.0 < pe < 15.0):
            return False, f"PE {pe} out of range"
            
        op_margin = info.get('operatingMargins')
        if op_margin is None or op_margin < 0.10:
            return False, f"Op Margin {op_margin} < 10%"
            
        roe = info.get('returnOnEquity')
        if roe is None or roe < 0.10:
            return False, f"ROE {roe} < 10%"
            
        return True, {"pe": pe, "op_margin": op_margin, "roe": roe}
    except Exception as e:
        return False, str(e)

for market, tickers in [("TW", tw_tickers), ("US", us_tickers), ("HK", hk_tickers), ("JP", jp_tickers)]:
    print(f"--- {market} ---")
    random.shuffle(tickers)
    found = 0
    attempts = 0
    for tk in tickers:
        attempts += 1
        ok, data = check_stock(tk)
        if ok:
            print(f"FOUND {tk}: {data}")
            found += 1
            if found == 5:
                break
        else:
            pass #print(f"REJECTED {tk}: {data}")
    print(f"{market} Found {found}, Attempts: {attempts}")
