title DBDump Backup Zip
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%

move "%TradeAnalysis_DBDumpZipPath%latest_DBDumpZip\*.*" "%TradeAnalysis_DBDumpZipPath%"

"%TradeAnalysis_7zip%" a -tzip "%TradeAnalysis_DBDumpZipPath%latest_DBDumpZip\DBDump_%TradeAnalysis_DBDumpZipSuffix%_%mydate%.zip" "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
"%TradeAnalysis_7zip%" a -tzip "%TradeAnalysis_DBDumpZipPath%latest_DBDumpZip\DBDump_%TradeAnalysis_DBDumpZipSuffix%_%mydate%_ib.zip" "%TradeAnalysis_DBDumpPath%*%mydate%_ib.sql"
rem del "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
pause