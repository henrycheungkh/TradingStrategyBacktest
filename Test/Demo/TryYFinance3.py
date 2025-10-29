import time
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

def get_eod(symbol, period="6mo", interval="1d", attempts=3):
    last_exc = None
    for i in range(attempts):
        try:
            df = yf.download(symbol, period=period, interval=interval,
                             progress=False, threads=False)  # no session=
            if not df.empty:
                return df
        except YFRateLimitError:
            time.sleep(5*(i+1))
        except Exception as e:
            last_exc = e
            time.sleep(2)
    raise RuntimeError(f"No price data for {symbol}") from last_exc

df = get_eod("HSBA.L")
print(df.tail())
