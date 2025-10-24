title Zip Ticker List
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%
SET PYTHONPATH=%TradeAnalysis_ProjectPath%


"%TradeAnalysis_7zip%" a -tzip "G:\temp\TickerListForGapperScanning%mydate%.zip" "G:\temp\TickerListForGapperScanning%mydate%.csv"

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Email_Ticker_List.py"

rem del "G:\temp\TickerListForGapperScanning%mydate%.csv"
rem pause
rem timeout /t 28800