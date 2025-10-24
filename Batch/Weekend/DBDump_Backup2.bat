title DBDump Backup
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" -u root finance_fdata_price_30min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_30min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_ib_%mydate%_ib.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" -u root finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" -u root finance_fdata_price_dayend_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_dayend_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_ib_%mydate%_ib.sql")


"%TradeAnalysis_7zip%" a -tzip "%TradeAnalysis_DBDumpZipPath%DBDump_%TradeAnalysis_DBDumpZipSuffix%_%mydate%.zip" "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
"%TradeAnalysis_7zip%" a -tzip "%TradeAnalysis_DBDumpZipPath%DBDump_%TradeAnalysis_DBDumpZipSuffix%_%mydate%_ib.zip" "%TradeAnalysis_DBDumpPath%*%mydate%_ib.sql"
rem del "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
pause