title Scan US Gappers
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\StandaloneUSStockGapperScanner.py"


rem %TradeAnalysis_ProjectPath%\Batch\Daily\DailyIBDownloadTodayPatch.bat

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "1 min" "3 D" DirectUpload -1 30Y
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadFuturesFromIB.py" "10 secs" "3 D" DirectUpload -1 2YY

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Screen_GapperByIB.py" WebSynOff
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Screen_GapperByIB.py" WebSynOn SOFI,FUTU,VST,FRPT,RRC,STAA,SEB,EYE


rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\ConsolidatedIBProcessor.py"
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Screen_GapperByIB.py" WebSynOn


rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2021-10-05 2000 0 "TRADES" "2 D" DirectUpload
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 day" 2021-10-05 2000 0 "TRADES" "5 D" DirectUpload

rem pause
rem timeout /t 28800

timeout /t 7200