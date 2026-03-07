# Copilot / AI Agent Instructions for TradingStrategyBacktest

Purpose
- Help an AI coding agent quickly become productive across the two analysis projects in this workspace: `TradingStrategyBacktest` and `FuturesAnalysis`.

Big picture
- Two related codebases live side-by-side: the main data/automation/backtest project in `TradingStrategyBacktest/` and supplementary analysis code in `FuturesAnalysis/`.
- Data flow: market data is downloaded (IB / Yahoo) into local folders (env vars `TradeAnalysis_DownloadFileBuffer`, `TradeAnalysis_DownloadFuturesFileBuffer`), batch scripts in `Batch/` pick up files and upload to MySQL (env var `TradeAnalysis_mysql`). Analysis/backtests read CSVs or DB exports and write CSV results.
- Key integration points: IB API (`ibapi`), MySQL (`pymysql`), Yahoo (`yfinance`, `yahoo_fin`), optional GPU (`pycuda`). See [TradingStrategyBacktest/README.md](TradingStrategyBacktest/README.md) and [TradingStrategyBacktest/requirements.txt](TradingStrategyBacktest/requirements.txt).

Where to look first (quick tour)
- Environment & setup: [TradingStrategyBacktest/README.md](TradingStrategyBacktest/README.md) and `requirements.txt`.
- Batch automation: `TradingStrategyBacktest/Batch/` (Daily / Weekend / DBDump / HealthCheck) — these `.bat` files implement the download/upload scheduling used in production.
- Core backtest base class: `TradingStrategyBacktest/Adhoc Analysis/AdhocBacktestKeyLevelBaseClass.py` (instantiate or subclass to implement strategies).
- Reusable utilities: `FuturesAnalysis/lib/AdhocBacktestLib.py` and `FuturesAnalysis/util/data_reading_lib.py` (examples of helper functions and CSV/ZIP readers).

Project-specific conventions and patterns
- DataFrame-first style: functions and classes treat price data as pandas DataFrames named with `df_` prefixes (e.g., `df_SingleSeries`, `df_KeyLevels`). Preserve column names such as `tDateTime`, `TimeInStandardUnit`, `price`, `PnL` when modifying code.
- `getPriceInSingleSeries()` pattern: present in both `AdhocBacktestKeyLevelBaseClass.py` and `FuturesAnalysis/lib/AdhocBacktestLib.py`. Keep behavior consistent if refactoring (it creates 3 price-step rows per candle and sorts by `tDateTime`).
- Parameterization: backtests accept nested `ParameterList` dicts that are recursively enumerated by `RunBacktest()` — follow the same dict-based parameter API when writing automated experiments.
- Debug/export conventions: many classes accept `DebugExportFilepath` and `ResultSummaryExportFilepath` to persist intermediate results — add new debugging outputs using these parameters rather than changing existing I/O paths.
- GPU mode: classes accept `GPUMode` booleans; optional `pycuda` usage should remain optional and gated behind this flag.

Developer workflows (concrete commands)
- Install environment:
```powershell
conda create -n tsbacktest python=3.10 -y
conda activate tsbacktest
pip install -r TradingStrategyBacktest/requirements.txt
```
- Required external services: install and configure MySQL Community Server; set `TradeAnalysis_mysql`, `TradeAnalysis_DownloadFileBuffer`, `TradeAnalysis_DownloadFuturesFileBuffer`, `TradeAnalysis_mysqldump` environment variables before running batch automation.
- Run daily download/upload batches on Windows: run the `.bat` files in `TradingStrategyBacktest/Batch/Daily/` (e.g. `DailyIBDownload.bat`, `ADailyIBDataDBUploader*.bat`) using Task Scheduler or PowerShell.

Editing guidance for AI agents
- Preserve public APIs and DataFrame schemas: changing column names or the signature of `getPriceInSingleSeries()` has wide impact.
- Prefer adding new helper modules under `FuturesAnalysis/lib/` or `TradingStrategyBacktest/Adhoc Analysis/` rather than editing the base classes in-place unless fixing a bug.
- When introducing changes that affect data flow (new env vars, new CSV columns, new DB tables), update `README.md` and any `.bat` files that depend on them.
- There are no unit tests in the repo; validate changes by running a small manual backtest with a trimmed CSV and by checking produced CSV outputs (use `DebugExportFilepath`).

Examples (concrete snippets to emulate)
- Instantiate the base backtest flow (see `AdhocBacktestKeyLevelBaseClass`): create `ParameterList` dict and call the class constructor with `PriceDataFilepath`, `Ticker`, and `ParameterList` to run the nested grid search pattern used throughout.
- Use `FuturesAnalysis/util/data_reading_lib.py` for downloading+reading zipped CSVs; it demonstrates downloading into memory and returning a pandas DataFrame.

What not to do
- Do not rename core DataFrame columns (e.g., `tDateTime`, `price`, `PnL`) without touching all consumers.
- Do not assume Linux tooling or systemd timers — the repo targets Windows `.bat` automation and Task Scheduler.

If you need clarification
- Ask which script or batch the user wants to run, or show a one-file reproduction using a small CSV. I can also add runnable examples or small harness scripts if you want.

References
- [TradingStrategyBacktest/README.md](TradingStrategyBacktest/README.md)
- [TradingStrategyBacktest/Adhoc Analysis/AdhocBacktestKeyLevelBaseClass.py](TradingStrategyBacktest/Adhoc Analysis/AdhocBacktestKeyLevelBaseClass.py)
- [TradingStrategyBacktest/requirements.txt](TradingStrategyBacktest/requirements.txt)
- [FuturesAnalysis/lib/AdhocBacktestLib.py](FuturesAnalysis/lib/AdhocBacktestLib.py)
- [FuturesAnalysis/util/data_reading_lib.py](FuturesAnalysis/util/data_reading_lib.py)
