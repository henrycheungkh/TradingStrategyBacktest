set mydate=%date:~6,4%%date:~3,2%%date:~0,2%
echo %mydate%
rem D:\xampp\mysql\bin\mysqldump -u root -p finance > d:\Shared\TAHistoricalData\DBDump\DBDump_finance_oneoff_%mydate%.sql
D:\xampp\mysql\bin\mysqldump -u root finance > d:\Shared\TAHistoricalData\DBDump\DBDump_finance_oneoff_%mydate%.sql
pause