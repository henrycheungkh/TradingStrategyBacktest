title DBDump Futures 1min 2019 2022


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info --no-create-db -u root finance_fdata_fut_hist > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_1min_2019_2022.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info --no-create-db -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_1min_2019_2022.sql")

pause