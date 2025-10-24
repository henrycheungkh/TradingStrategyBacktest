set DateString=20220104

SET /P AREYOUSURE=It will overwrite data as of %DateString%, are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END


set DBName=fdata_fut_hist_10secs_2021
if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%.sql)

:END

pause