title DBDump Backup Master
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" -u root finance_fdata_master > "%TradeAnalysis_DBDumpPath%DBDump_finance_fdata_master_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" -u root -p%TradeAnalysis_DBPassword% finance_fdata_master > "%TradeAnalysis_DBDumpPath%DBDump_finance_fdata_master_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_dayend > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_dayend > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_dayend_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min_fx > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_fx_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_fx > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_fx_%mydate%.sql")

if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root finance_fdata_price_30min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_%mydate%.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-locks --insert-ignore --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_30min > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_%mydate%.sql")

pause