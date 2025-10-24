set DateString=20211118

SET /P AREYOUSURE=It will overwrite data as of %DateString%, are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

set DBName=fdata_fut_hist_kirk

if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_kirk_-1-2.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_kirk_-1-2.sql)


:END

pause