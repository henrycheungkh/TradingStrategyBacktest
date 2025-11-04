title Health Check IB Futures Only
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

"%TradeAnalysis_PythonPath%" %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice
"%TradeAnalysis_PythonPath%" %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPriceHighestVolumeTime

rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%DownloadHealthCheck.py IBFuturesPriceByTicker
rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%DownloadHealthCheck.py IBStockPrice

echo %date%_%time%

pause