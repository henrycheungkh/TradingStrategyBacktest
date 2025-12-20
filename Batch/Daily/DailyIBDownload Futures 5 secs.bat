title IB Futures 5secs Download
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 NQ 20251027
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 NQ 20251028

set CaptureDate=20251219





"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 10Y %CaptureDate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 CL %CaptureDate%


goto :skip

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 RTY %CaptureDate%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 SI %CaptureDate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 YM %CaptureDate%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "3 D" DirectUpload -1 GC %CaptureDate%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 2YY %CaptureDate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 ES %CaptureDate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 NQ %CaptureDate%


rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "2 D" DirectUpload -1 HE %CaptureDate%
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "2 D" DirectUpload -1 SI %CaptureDate%

:skip

timeout /t 3000

rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice


timeout /t 24400
