title Daily IB Download
SET PYTHONPATH=%TradeAnalysis_ProjectPath%
rem set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
set mydate="20251031"

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 NQ

timeout /t 20000
