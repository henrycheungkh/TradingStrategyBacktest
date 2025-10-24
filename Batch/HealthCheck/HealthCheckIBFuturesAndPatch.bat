title Health Check IB Futures and Patch
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

%TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice UploadFuturesPatch


rem pause
timeout /t 10000
