set DBName=fdata_fut_hist_10secs_2021

if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < E:\TAHistoricalData\DBDump\DBDump_fdata_fut_hist_10secs\DBDump_fdata_fut_hist_10secs_2021.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < E:\TAHistoricalData\DBDump\DBDump_fdata_fut_hist_10secs\DBDump_fdata_fut_hist_10secs_2021.sql)

set DBName=fdata_fut_hist_10secs_2022


if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < E:\TAHistoricalData\DBDump\DBDump_fdata_fut_hist_10secs\DBDump_fdata_fut_hist_10secs_2022.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < E:\TAHistoricalData\DBDump\DBDump_fdata_fut_hist_10secs\DBDump_fdata_fut_hist_10secs_2022.sql)

:END

pause