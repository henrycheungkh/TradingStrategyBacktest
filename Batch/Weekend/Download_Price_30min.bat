title Download Price 30min
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" USOnly 300 30min weekly DirectUpload
rem rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" ExcludeUS 800 30min weekly DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" UKOnly 100 30min weekly DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" HKOnly 320 30min weekly DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" YahooStockPrice30min
pause

rem rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Download_Price.py" FXOnly 600 30min weekly DirectUpload
