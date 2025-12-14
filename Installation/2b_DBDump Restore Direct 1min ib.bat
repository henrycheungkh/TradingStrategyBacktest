set DateString=20251109

SET /P AREYOUSURE=It will overwrite data as of %DateString%, are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

rem set DBName=fdata_price_dayend_ib
rem if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysql%" -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%_ib.sql) else ("%TradeAnalysis_mysql%" -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%_ib.sql)


set DBName=fdata_price_1min_ib
if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysql%" --force -u %TradeAnalysis_DBUser% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%_ib.sql) else ("%TradeAnalysis_mysql%" --force -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_%DBName% < %TradeAnalysis_DBDumpPath%DBDump_%DBName%_%DateString%_ib.sql)

:END 

pause