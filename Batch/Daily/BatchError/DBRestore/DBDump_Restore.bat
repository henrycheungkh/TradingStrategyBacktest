rem %TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_recovered < %TradeAnalysis_DBDumpPath%DBDump_finance_20211011.sql
%TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_frec_fut_hist < %TradeAnalysis_DBDumpPath%DBDump_fdata_fut_hist_20211011.sql
rem %TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_fdata_recovered_price_1min < %TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_20211011.sql
rem %TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_fdata_recovered_price_1min_fx < %TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_fx_20211011.sql
rem %TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_fdata_recovered_price_1min_2020 < %TradeAnalysis_DBDumpPath%DBDump_fdata_price_1min_20211011.sql
rem %TradeAnalysis_mysql% -u %TradeAnalysis_DBUser% finance_fdata_recovered_price_30min_ib < %TradeAnalysis_DBDumpPath%DBDump_fdata_price_30min_ib_20211011.sql
pause