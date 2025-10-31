title Daily IB Download
SET PYTHONPATH=%TradeAnalysis_ProjectPath%
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 day" 2000 0 "TRADES" "5 D" DirectUpload

timeout /t 20000
