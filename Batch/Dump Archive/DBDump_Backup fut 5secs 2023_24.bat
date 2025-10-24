title DBDump Futures 5secs 2023_24


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info --no-create-db -u root finance_fdata_fut_hist_5secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_5secs_2023_24.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info --no-create-db -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_5secs > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_5secs_2024.sql")

pause