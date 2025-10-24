rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%Download_Price.py" FXOnly 7000 dayend 3 DirectUpload
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%Download_Price.py" USOnly 7000 dayend 3 DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%Download_Price.py" ExcludeUS 7000 dayend 3 DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%DownloadHealthCheck.py" YahooStockPriceDayEnd
pause