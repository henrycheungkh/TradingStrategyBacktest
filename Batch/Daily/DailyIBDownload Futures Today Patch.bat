title Daily IB Download
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

@echo off

REM Set the specific date you want to check (format: YYYY-MM-DD)
set "specific_date=2023-06-23"

REM Get the current date
for /f "usebackq tokens=1" %%a in (`%SystemRoot%\System32\wbem\wmic.exe OS Get localdatetime ^| %SystemRoot%\System32\find.exe "."`) do set "current_date=%%a"

REM Extract the year, month, and day from the current date
set "current_year=%current_date:~0,4%"
set "current_month=%current_date:~4,2%"
set "current_day=%current_date:~6,2%"

REM Extract the year, month, and day from the specific date
set "specific_year=%specific_date:~0,4%"
set "specific_month=%specific_date:~5,2%"
set "specific_day=%specific_date:~8,2%"

REM Check if the current date matches the specific date
if "%current_year%"=="%specific_year%" if "%current_month%"=="%specific_month%" if "%current_day%"=="%specific_day%" (
    REM Your command to be executed if the dates match
    echo Today is the specific date!

    "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 30Y

    "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 30Y
    "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 ETHUSDRR

    "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 mins" "4 D" DirectUpload -1 10Y
    "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 mins" "4 D" DirectUpload -1 2YY
    "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "5 mins" "4 D" DirectUpload -1 30Y


) else (
    REM Your command to be executed if the dates do not match
    echo Today is not the specific date.
)

pause