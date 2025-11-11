title DBDump Backup
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_30min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_30min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_ib_%mydate%_ib.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_%mydate%_ib.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_dayend_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_ib_%mydate%_ib.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_dayend_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_ib_%mydate%_ib.sql")


pause