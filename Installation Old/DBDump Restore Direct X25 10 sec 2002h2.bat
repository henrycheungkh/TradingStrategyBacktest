set DBName=fdata_fut_hist_10secs_2022_h2


if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < E:\TAHistoricalData\DBDump\DBDump_fdata_fut_hist_10secs\DBDump_fdata_fut_hist_10secs_2022h2.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < E:\TAHistoricalData\DBDump\DBDump_fdata_fut_hist_10secs\DBDump_fdata_fut_hist_10secs_2022h2.sql)

:END

pause