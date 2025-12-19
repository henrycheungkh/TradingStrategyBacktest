title Keep IB Gateway Alive
SET PYTHONPATH=%TradeAnalysis_ProjectPath%

:repeat

time /t

"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%InvestmentAnalytics\IB\Keep_IB_Gateway_Alive.py"

timeout /t 900

goto :repeat
