title Download Price dayend
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" FXOnly 7000 dayend 3 DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" HKOnly 200 dayend 3 DirectUpload
rem rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" ExcludeUS 1000 dayend 3 DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" UKOnly 200 dayend 3 DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" USOnly 1000 dayend 3 DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" YahooStockPriceDayEnd
pause