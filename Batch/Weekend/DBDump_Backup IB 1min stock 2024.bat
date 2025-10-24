title DBDump Backup finance_fdata_price_1min_ib_2024
set mydate=%date:~10,4%%date:~4,2%%date:~7,2%
echo %mydate%


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info -u root finance_fdata_price_1min_ib_2024 > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_2024.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_ib_2024 > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_2024.sql")

rem del "%TradeAnalysis_DBDumpPath%*%mydate%.sql"
pause