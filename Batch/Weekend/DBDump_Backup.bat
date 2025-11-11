title DBDump Backup
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" -u root finance_fdata_master > "%TradeAnalysis_DBDumpPath%DBDump_finance_fdata_master_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" -u root -p%TradeAnalysis_DBPassword% finance_fdata_master > "%TradeAnalysis_DBDumpPath%DBDump_finance_fdata_master_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_dayend > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_dayend > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min_fx > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_fx_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_fx > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_fx_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_30min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_30min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_ib_%mydate%_ib.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_dayend_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_dayend_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_ib_%mydate%_ib.sql")


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist_10secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_10secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist_5secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_5secs_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_5secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_5secs_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_30min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_30min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_%mydate%.sql")



move "%TradeAnalysis_DBDumpZipPath%latest_DBDumpZip\*.*" "%TradeAnalysis_DBDumpZipPath%"

"%TradeAnalysis_7zip%" a -tzip "%TradeAnalysis_DBDumpZipPath%latest_DBDumpZip\DBDump_%TradeAnalysis_DBDumpZipSuffix%_%mydate%.zip" "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
"%TradeAnalysis_7zip%" a -tzip "%TradeAnalysis_DBDumpZipPath%latest_DBDumpZip\DBDump_%TradeAnalysis_DBDumpZipSuffix%_%mydate%_ib.zip" "%TradeAnalysis_DBDumpPath%*%mydate%_ib.sql"
rem del "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
pause