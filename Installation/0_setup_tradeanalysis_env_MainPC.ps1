# ==============================================
# TradeAnalysis Environment Variable Setup Script
# ==============================================
Write-Host "Setting up TradeAnalysis environment variables..." -ForegroundColor Cyan

$envVars = @{
    "TradeAnalysis_7zip"                       = "C:\Program Files\7-Zip\7z"
    "TradeAnalysis_CCompilerPath"              = "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"
    "TradeAnalysis_CUDAThreadCount"            = "1024"
    "TradeAnalysis_DBDumpPath"                 = "C:\TradeAnalysisProject\DBDump\"
    "TradeAnalysis_DBDumpZipPath"              = "C:\TradeAnalysisProject\DBDumpZip\"
    "TradeAnalysis_DBDumpZipSuffix"            = "Henry"
    "TradeAnalysis_DBHost"                     = "localhost"
    "TradeAnalysis_DBPassword"                 = "ZAQ!2wsx"
    "TradeAnalysis_DBPort"                     = "3306"
    "TradeAnalysis_DBUser"                     = "root"
    "TradeAnalysis_DownloadFileBuffer"         = "C:\TradeAnalysisProject\TAHistoricalData\"
    "TradeAnalysis_DownloadFuturesFileBuffer"  = "C:\TradeAnalysisProject\FuturesHistoricalData\"
    "TradeAnalysis_IB_API_clientId"            = "123"
    "TradeAnalysis_IB_API_Futures_clientId"    = "123"
    "TradeAnalysis_IB_API_KeepAlive_clientId"  = "100"
    "TradeAnalysis_IB_API_hostname"            = "127.0.0.1"
    "TradeAnalysis_IB_API_port"                = "7496"
    "TradeAnalysis_LocalTimezone"              = "Europe/London"
    "TradeAnalysis_mysql"                      = "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql"
    "TradeAnalysis_mysqldump"                  = "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump"
    "TradeAnalysis_ProjectPath"                = "C:\Projects\TradingStrategyBacktest\"
    "TradeAnalysis_PythonPath"                 = "c:\ProgramData\anaconda3\python.exe"
    "TradeAnalysis_USGapperScanEndTime"        = "10:00"
}

foreach ($key in $envVars.Keys) {
    $value = $envVars[$key]
    [Environment]::SetEnvironmentVariable($key, $value, "User")
    Write-Host "Set $key = $value"
}

Write-Host "`nAll TradeAnalysis environment variables have been set successfully." -ForegroundColor Green
