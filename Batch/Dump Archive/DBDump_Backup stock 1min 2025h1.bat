title DBDump Stocks 1min 2025h1


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info --no-create-db -u root finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_2025h1.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info --no-create-db -u root -p%TradeAnalysis_DBPassword% finance_fdata_price_1min_ib > "%TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_ib_2025h1.sql")

pause