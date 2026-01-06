title DBDump Backup
set mydate=2025

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist_10secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_10secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_%mydate%.sql")


pause