import time
import requests
import yfinance as yf

def get_eod(symbol, period="6mo", interval="1d", attempts=3):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    last_exc = None

    for i in range(attempts):
        try:
            df = yf.download(symbol, period=period, interval=interval,
                             progress=False, threads=False, session=s)
            if df is not None and not df.empty:
                return df
        except Exception as e:           # generic fallback
            last_exc = e
            time.sleep(2)

    raise RuntimeError(f"No price data for {symbol}") from last_exc

ticker = "HSBA.L"
df = get_eod(ticker)
print(df.tail())
