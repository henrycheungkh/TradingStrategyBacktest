title Daily IB Download Patch
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ES

pause
