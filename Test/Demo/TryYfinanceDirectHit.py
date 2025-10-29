import requests
url = "https://query2.finance.yahoo.com/v8/finance/chart/HSBA.L?range=6mo&interval=1d"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
print("status:", r.status_code, r.headers.get("content-type"))
print(r.text[:400])
