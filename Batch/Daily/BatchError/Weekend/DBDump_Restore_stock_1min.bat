set mydate=%date:~6,4%%date:~3,2%%date:~0,2%
echo %mydate%
D:\xampp\mysql\bin\mysql -u root -p finance_stock_1min < D:\Shared\TAHistoricalData\DBDump\DBDump_20210724.sql
pause