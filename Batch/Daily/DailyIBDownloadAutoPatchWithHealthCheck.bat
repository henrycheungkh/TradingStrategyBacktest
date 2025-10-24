title Daily IB Download Today Auto Patch With Health Check
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

@echo off

%TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice UploadFuturesPatch
%TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPriceHighestVolumeTime

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DailyFuturesAutoPatch.py"

pause
