title Daily IB Download Today Patch
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

@echo off

rem -- if missing data on 20230918, use 20230919 as parameter as below
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\DownloadUSStockPriceFromIB.py" "1 min" 2000 0 "TRADES" "2 D" DirectUpload 20250909



echo Today Patch finished
pause
