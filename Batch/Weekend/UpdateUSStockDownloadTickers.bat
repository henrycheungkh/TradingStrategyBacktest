title Update US Stock Download Tickers
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\UpdateUSStockDownloadTickers.py" "1 day" 2023-01-01
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\UpdateUSStockDownloadTickers.py" "30 mins" 2023-01-01
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\UpdateUSStockDownloadTickers.py" "1 min" 2023-01-01

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\UpdateUSStockDownloadTickers.py" "1 day"
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\UpdateUSStockDownloadTickers.py" "30 mins"
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\UpdateUSStockDownloadTickers.py" "1 min"

pause
rem timeout /t 7200
