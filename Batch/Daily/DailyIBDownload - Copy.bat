title Daily IB Download
SET PYTHONPATH=%TradeAnalysis_ProjectPath%
rem set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
rem set mydate=20251208



:: Get the current hour (24-hour format)
for /f "tokens=1 delims=:" %%a in ("%time%") do set hour=%%a

:: Remove leading zero (if any)
if "%hour:~0,1%"=="0" set hour=%hour:~1%

:: Check if it's morning or afternoon
if %hour% lss 12 (
    echo Good morning!
rem     for /f %%a in ('powershell -NoProfile -Command "(Get-Date).AddDays(-1).ToString(\"yyyyMMdd\")"') do set YESTERDAY=%%a
    for /f %%a in ('powershell -NoProfile -Command "(Get-Date).AddDays(-1).ToString(\"yyyyMMdd\")"') do set mydate=%%a

rem     echo %YESTERDAY%

rem     set mydate=%YESTERDAY%
) else (
    echo Good afternoon!
    set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
)



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
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 HE



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
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 CT

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

rem timeout /t 3000

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBFuturesPrice
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice30mins
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPriceDayEnd

rem timeout /t 3000

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice1min
rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice

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

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 mins" "3 D" DirectUpload

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice30mins
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPriceDayEnd
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py" IBStockPrice1min
rem timeout /t 3000
rem %TradeAnalysis_PythonPath% %TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadHealthCheck.py IBFuturesPrice
start "" %TradeAnalysis_ProjectPath%\Batch\HealthCheck\HealthCheckIBFuturesOnly.bat


rem pause
timeout /t 20000
rem timeout /t 7200
