title Daily IB Download
SET PYTHONPATH=%TradeAnalysis_ProjectPath%
rem set mydate=%date:~10,4%%date:~4,2%%date:~7,2%

set mydate="20251031"


if "%mydate%"=="20251018" (

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "2 D" DirectUpload -1 YM 20251014
  set mydate="20251015"
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 GC %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 SI %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 ES %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 NQ %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 RTY %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 YM %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 2YY %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 10Y %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 CL %mydate%
  set mydate="20251018"

)  

if "%mydate%"=="20250619" (

  set mydate="20250911"
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 CL 20250619
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 GC 20250619
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 SI 20250619
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 10Y 20250619

  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 CT 20250616
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 KC 20250616
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 NG 20250616
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 PL 20250616
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 RB 20250616
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 RTY 20250616
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 SI 20250616


   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ES 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ETHUSDRR 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HE 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HG 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HO 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 MBT 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 NG 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 NQ 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 RTY 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 SI 20250616
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HE 20250619
   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 KC 20250619

)

rem rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 10000000 2021-07-28 2000 0 "TRADES,BID,ASK" "2 D" DirectUpload

rem rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 10000000 2021-10-05 2000 0 "TRADES" "2 D" DirectUpload


rem rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload


for /F "tokens=1" %%i in ('date /t') do set day=%%i

if "%day%"=="Sat" (
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 day" 2000 0 "TRADES" "5 D" DirectUpload
  rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 2000 0 "TRADES" "5 D" DirectUpload
  rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "3 D" DirectUpload

) else (
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 day" 2000 0 "TRADES" "3 D" DirectUpload
  rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 2000 0 "TRADES" "3 D" DirectUpload
  rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "2 D" DirectUpload
)


"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 mins" "3 D" DirectUpload


"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ES
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 GC
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 2YY
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 10Y
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 30Y





"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 GC
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 SI
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 CL
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 NG

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ES
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 NQ
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 RTY
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 YM
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZN
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZT
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 RB
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HO
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 PL
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZW
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZR
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZL
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZS
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ZC
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 KC
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HG
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 2YY
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 10Y
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 30Y



rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 mins" "3 D" DirectUpload -1 ES

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload

REM "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ES
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 GC
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 NQ
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 RTY
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "4 D" DirectUpload -1 YM
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ZN
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ZT
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 SI
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 CL
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 NG
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 RB
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 HO
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 PL
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 HE
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ZW
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ZR
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ZL
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ZS
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ZC
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 KC
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 HG
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 GF
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 OJ

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 GC
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 SI
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 ES
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 NQ
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 RTY
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 YM
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 2YY
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 10Y
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 CL


"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 MBT
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 MET
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ETHUSDRR


"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 MBT
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 MET
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 ETHUSDRR

for /F "tokens=1" %%i in ('date /t') do set day=%%i

if "%day%"=="Sat" (
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 2000 0 "TRADES" "5 D" DirectUpload
  rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 day" 2000 0 "TRADES" "5 D" DirectUpload

  start "" %TradeAnalysis_ProjectPath%\Batch\HealthCheck\HealthCheckIBFuturesAndPatch.bat
  rem start "" %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice UploadFuturesPatch

  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "3 D" DirectUpload
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "2 D" DirectUpload 20250113

) else (
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "30 mins" 2000 0 "TRADES" "3 D" DirectUpload
  rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 day" 2000 0 "TRADES" "3 D" DirectUpload

  start "" %TradeAnalysis_ProjectPath%\Batch\HealthCheck\HealthCheckIBFuturesAndPatch.bat
  rem start "" %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice UploadFuturesPatch

rem   "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "3 D" DirectUpload
  "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "2 D" DirectUpload
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "2 D" DirectUpload 20250113
)




rem %TradeAnalysis_ProjectPath%\Batch\Daily\DailyIBDownloadTodayPatch.bat
rem start "" %TradeAnalysis_ProjectPath%\Batch\Daily\DailyIBDownloadAutoPatchWithHealthCheck.bat
start "" %TradeAnalysis_ProjectPath%\Batch\Daily\DailyIBDownloadAutoPatch.bat


rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice
rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPriceHighestVolumeTime

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DailyFuturesAutoPatch.py"

timeout /t 3000

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBFuturesPrice
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice30mins
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPriceDayEnd

timeout /t 3000

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice1min
%TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice

echo %mydate%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 GC %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 SI %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 ES %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 NQ %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 RTY %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 YM %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 2YY %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 10Y %mydate%
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 secs" "2 D" DirectUpload -1 CL %mydate%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice30mins
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPriceDayEnd
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice1min
rem timeout /t 3000
rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice
start "" %TradeAnalysis_ProjectPath%\Batch\HealthCheck\HealthCheckIBFuturesOnly.bat


rem pause
timeout /t 20000
rem timeout /t 7200
