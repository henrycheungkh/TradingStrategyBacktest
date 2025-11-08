title Download FX Price 2min
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" FXOnly 400 2min 0 DirectUpload
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%DownloadHealthCheck.py" YahooStockPrice1min
pause