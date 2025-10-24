title Daily IB Download Stock 30min
SET PYTHONPATH=%TradeAnalysis_ProjectPath%


"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 2022-09-18 2000 0 "TRADES" "5 D" DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice

pause