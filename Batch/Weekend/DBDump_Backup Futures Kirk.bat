title DBDump Backup Futures from Kirk
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" -u root finance_fdata_fut_hist_kirk > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_kirk_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_kirk > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_kirk_%mydate%.sql")


"%TradeAnalysis_7zip%" a -tzip "%TradeAnalysis_DBDumpZipPath%DBDump_%TradeAnalysis_DBDumpZipSuffix%_%mydate%_kirk.zip" "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
rem del "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
pause