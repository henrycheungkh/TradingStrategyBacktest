title Daily IB Download Stock 30min
SET PYTHONPATH=%TradeAnalysis_ProjectPath%


"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 2025-10-18 2000 0 "TRADES" "3 D" DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice

pause