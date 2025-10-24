title Send Strategy Alert
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\Batch\Email_Strategy_Alert_Level.py"

timeout /t 60
rem pause
