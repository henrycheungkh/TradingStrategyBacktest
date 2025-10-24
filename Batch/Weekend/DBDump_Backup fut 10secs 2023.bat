title DBDump Futures 10 secs 2023


if %TradeAnalysis_DBPassword%==None ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info -u root finance_fdata_fut_hist_10secs_2023 > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_2023.sql") else ("%TradeAnalysis_mysqldump%" --skip-add-drop-table --no-create-info -u root -p%TradeAnalysis_DBPassword% finance_fdata_fut_hist_10secs_2023 > "%TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_10secs_2023.sql")

pause