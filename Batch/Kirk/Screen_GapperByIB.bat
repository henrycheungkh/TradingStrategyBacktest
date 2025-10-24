title Scan US Gappers
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%Screen_GapperByIB.py" WebSynOff SOFI,FUTU,VST,FRPT,RRC,STAA,SEB,EYE
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%Screen_GapperByIB.py" WebSynOff
rem "%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%Screen_GapperByIB.py" WebSynOn
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%DownloadUSStockPriceFromIB.py" "1 min" 2021-10-05 2000 0 "TRADES" "2 D" DirectUpload
"%TradeAnalysis_PythonPath%" "%TradeAnalysis_ProjectPath%DownloadUSStockPriceFromIB.py" "1 day" 2021-10-05 2000 0 "TRADES" "5 D" DirectUpload
pause