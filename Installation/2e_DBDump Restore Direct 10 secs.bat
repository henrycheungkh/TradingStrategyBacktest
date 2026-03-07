rem set DateString=20260104
set DateString=2022


SET /P AREYOUSURE=It will overwrite data as of %DateString%, are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END






set DBName=fdata_fut_hist_10secs
if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysql%" --force -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%.sql) else ("%TradeAnalysis_mysql%" --force -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%.sql)


:END

pause