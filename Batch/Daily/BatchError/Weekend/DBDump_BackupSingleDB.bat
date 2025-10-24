rem D:\ProgramData\Anaconda3\python.exe D:\PythonProjects\TradeAnalysis\DownloadHealthCheck.py
set mydate=%date:~6,4%%date:~3,2%%date:~0,2%
echo %mydate%
rem D:\xampp\mysql\bin\mysqldump -u root finance > d:\Shared\TAHistoricalData\DBDump\DBDump_finance_%mydate%.sql
D:\xampp\mysql\bin\mysqldump -u root finance_fdata_price_1min > d:\Shared\TAHistoricalData\DBDump\DBDump_fdata_price_1min_%mydate%.sql
rem D:\xampp\mysql\bin\mysqldump -u root finance_fdata_fut_hist > d:\Shared\TAHistoricalData\DBDump\DBDump_fdata_fut_hist_%mydate%.sql
rem D:\xampp\mysql\bin\mysqldump -u root finance_fdata_price_30min_ib > d:\Shared\TAHistoricalData\DBDump\DBDump_fdata_price_30min_ib_%mydate%.sql

rem D:\xampp\mysql\bin\mysqldump -u root finance_fdata_price_1min_2021_h1 > d:\Shared\TAHistoricalData\DBDump\DBDump_fdata_price_1min_2021_h1_%mydate%.sql

pause