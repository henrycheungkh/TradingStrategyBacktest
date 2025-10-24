set DateString=20230107

SET /P AREYOUSURE=It will overwrite data as of %DateString%, are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END


rem set DBName=fdata_master
rem if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_finance_%DBName%_%DateString%.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_finance_%DBName%_%DateString%.sql)

set DBName=fdata_fut_hist
if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%.sql)


rem set DBName=fdata_fut_hist_10secs
rem if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%.sql)


:END

pause