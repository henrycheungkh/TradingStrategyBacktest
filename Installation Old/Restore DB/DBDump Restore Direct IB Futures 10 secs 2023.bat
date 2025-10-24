title DBDump Restore IB Futures 10 secs 2023


set DBName=fdata_fut_hist_10secs_2023
if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%.sql)

:END

pause