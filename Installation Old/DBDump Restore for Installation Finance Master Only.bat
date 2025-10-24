if %TradeAnalysis_DBPassword%==None (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_fdata_master < %TradeAnalysis_DBDumpPath%DBDump_finance_fdata_master_20211118.sql) else (%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% -p%TradeAnalysis_DBPassword% finance_fdata_master < %TradeAnalysis_DBDumpPath%DBDump_finance_fdata_master_20211118.sql)

pause