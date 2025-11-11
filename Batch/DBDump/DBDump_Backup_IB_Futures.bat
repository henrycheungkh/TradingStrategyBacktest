title DBDump Backup
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_%mydate%.sql")


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist_10secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_10secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist_5secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_5secs_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_5secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_5secs_%mydate%.sql")

pause