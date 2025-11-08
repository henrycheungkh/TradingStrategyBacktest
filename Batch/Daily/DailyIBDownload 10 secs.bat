title IB Futures 10 secs Download
SET PYTHONPATH=%TradeAnalysis_ProjectPath%


set CaptureDate=20251107

   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ES %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ETHUSDRR %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HE %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HG %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HO %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 MBT %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 NG %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 NQ %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 RTY %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 SI %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HE %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 KC %CaptureDate%

   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 YM %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 PL %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 RB %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZL %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZN %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZR %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZS %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZT %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZW %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 GC %CaptureDate%
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 CL %CaptureDate%



   rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 GC 20251029




timeout /t 3000

rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice


timeout /t 24400
