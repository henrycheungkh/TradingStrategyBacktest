set DBName=fdata_fut_hist_10secs_2023_h1


if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < G:\TradeAnalysisProject\DBDump\DBDump_fdata_fut_hist_10secs_2023_h1.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < G:\TradeAnalysisProject\DBDump\DBDump_fdata_fut_hist_10secs_2023_h1.sql)

:END

pause