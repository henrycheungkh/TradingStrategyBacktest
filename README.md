Trade Strategy Backtest System

This is a project for first reaping price data from IB and Yahoo Finance and store them up.  Next stage would be to develop analysis on them.


1. Application to be installed
Core

- MySQL Community Server LTS
  - my.ini settings
    - secure-file-priv=""
    - set innodb_buffer_pool_size
    - require_secure_transport=OFF

- Python (usually by Anaconda)
  https://www.anaconda.com/products/individual

- Python Driver for MySQL
  https://www.mysql.com/products/connector/

- IB Application
  
  Recommended IB Gateway, on top of the usual trading workstation platform you use
  

- IB Python API
  For example, but refer to official release by IB
    https://interactivebrokers.github.io/
    https://stackoverflow.com/questions/48470613/adding-the-ibapi-library-to-pythonpath-module-in-spyder-python-3-6
  to test
    from ibapi.client import EClient

Optional

- 7Zip
  https://www.7-zip.org/download.html

2. Python Package installation

Refer to the requirements.txt, which is mainly the below

Core

pip install pymysql
pip install yfinance
pip install ibapi
pip install yahoo_fin
pip install yahoo_earnings_calendar
pip install requests_html

pip install pymysql yfinance ibapi yahoo_fin yahoo_earnings_calendar requests_html



Optional

pip install GoogleNews
pip install newspaper3k
pip install tensorflow

- CUDA

https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html#installing-cuda-development-tools

install Visual Studio

pip install pycuda

Probably more, but I cannot remember them all.  Let's first try to run, and if there is an error, let me know and we can see which one is missing.

3. Build folder structure and set Environment Variable

Environment Variable: TradeAnalysis_DownloadFileBuffer
  Path to the IB downloaded US stock data, before uploading to MySQL Server.  Create a folder first, and set the path as value to this variable

Environment Variable: TradeAnalysis_DownloadFuturesFileBuffer
  Path to the IB downloaded US futures data, before uploading to MySQL Server.  Create a folder first, and set the path as value to this variable

Environment Variable: TradeAnalysis_mysql
  Path to the MySQL Dumped data.  Create a folder first, and set the path as value to this variable

Environment Variable: TradeAnalysis_mysqldump
  Path to the zipped MySQL Dumped data.  Create a folder first, and set the path as value to this variable.  Create a subfolder of "latest_DBDumpZip" inside

Take reference to the powerscript in the Installation folder.  Modify it accordingly and run to setup the necessary environment variables.

4. Create Database

Use the SQL script 1_CreateDB_Live.sql in the Installation folder, to create the empty databases for the database framework 

5. Batches for running 

Batch\Daily\Download_Tickers.bat

The batch to download/reap stock tickers from the web.
Recommend to schedule and run it daily.

Batch\Daily\ADailyIBDataDBUploader.bat
Batch\Daily\ADailyIBDataDBUploaderHighPriority.bat
Batch\Daily\ADailyIBDataDBUploaderMediumPriority.bat

These 3 batch files together keep scanning for downloaded IB data need to be uploaded to the MySQL DB.
Start them first so the keep looping the scan

Batch\Daily\DailyIBDownload.bat

The batch which download the US stocks (daily, 30min, 1min) and US Futures (5 mins, 1 mins, 10 secs, 5 secs) and save the data to local drive, which will be uploaded to MySQL DB later by the scanner as above mentioned.
Can set a scheduler to trigger this task daily

Batch\Daily\Keep_IB_Gateway_Alive.bat

The batch to keep looping to ping the IB API about every 15 mins, to help to keep it alive.  Can trigger it and keep it looping if IB Gateway/API frequently disconnect its market data connection.

Batch\Daily\Download_FXPrice_1min.bat

The batch which download FX Spot prices (1min) from Yahoo Finance and upload to the MySQL DB.
Can set a scheduler to trigger this task daily

Batch\Weekend\Download_Price_dayend.bat
Batch\Weekend\Download_Price_30min.bat

The batch which download Stock prices (daily, 30mins) (HK Stocks, London Stocks, US Stocks (not working well)) from Yahoo Finance and upload to the MySQL DB.
Can set a scheduler to trigger this task, recommended weekly and with VPN, so Yahoo Finance is not blocking due to too heavy data request

Batch\DBDump\DBDump_Backup_IB_Futures.bat
Batch\DBDump\DBDump_Backup_IB_Stocks.bat
Batch\DBDump\DBDump_Backup_Master.bat

The batch to dump/export the whole MySQL server data.  Recommend to dump and archive data every year, and purge old price data (not data in DB finance_fdata_master) if it becomes too large.

Batch\DBDump\DBDump_Backup_Zip.bat

The batch to zip the MySQL dumped/exported data.

Batch\HealthCheck\HealthCheck.bat
Batch\HealthCheck\HealthCheck IB Futures Only.bat
Batch\HealthCheck\HealthCheck IB Stock Only.bat
Batch\HealthCheck\HealthCheck IB Stock 1 min Only.bat

These batches are for checking how many count of prices have been downloaded from IB per recent dates (and per tickers for Futures).  They can be used after running of DailyIBDownload.bat, to see how healthy/complete the download was.


