title DBDump Backup

set mydate=2025H2

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql")



pause