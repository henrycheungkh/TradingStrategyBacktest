CREATE DATABASE IF NOT EXISTS finance_fdata_master;

CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_5secs;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_30min_ib;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_ib;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_dayend_ib;

CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_fx;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_dayend;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_30min;

CREATE DATABASE IF NOT EXISTS finance_fdata_crypto_binance;

CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_2021;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_2022;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_2023;

CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_2020;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_2021_h1;


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `pending_db_upload_command` (
  `DBName` varchar(255) NOT NULL,
  `TableName` varchar(255) NOT NULL,
  `command` varchar(1000) NOT NULL,
  `Uploaded` int(11) NOT NULL,
  `Priority` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE finance_fdata_fut_hist.`fdata_fut_hist` (
  `ticker` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `instrumenttype` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `timeframe` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE finance_fdata_fut_hist.`fdata_fut_hist`
  ADD UNIQUE KEY `ticker_key` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`),
  ADD KEY `tick` (`ticker`);
COMMIT;

CREATE TABLE finance_fdata_fut_hist_10secs.`fdata_fut_hist` (
  `ticker` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `instrumenttype` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `timeframe` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE finance_fdata_fut_hist_10secs.`fdata_fut_hist`
  ADD UNIQUE KEY `ticker_key` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`),
  ADD KEY `tick` (`ticker`);
COMMIT;

CREATE TABLE finance_fdata_fut_hist_5secs.`fdata_fut_hist` (
  `ticker` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `instrumenttype` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `timeframe` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE finance_fdata_fut_hist_5secs.`fdata_fut_hist`
  ADD UNIQUE KEY `ticker_key` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`),
  ADD KEY `tick` (`ticker`);
COMMIT;


CREATE TABLE finance_fdata_price_1min.`fdata_price_1min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_1min.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;


CREATE TABLE finance_fdata_price_1min_fx.`fdata_price_1min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_1min_fx.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;

CREATE TABLE finance_fdata_price_30min.`fdata_price_30min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_30min.`fdata_price_30min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;

CREATE TABLE finance_fdata_price_30min_ib.`fdata_price_30min_ib` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_30min_ib.`fdata_price_30min_ib`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;

CREATE TABLE finance_fdata_price_1min_ib.`fdata_price_1min_ib` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_1min_ib.`fdata_price_1min_ib`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;


CREATE TABLE finance_fdata_price_dayend.`fdata_price_dayend` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` date NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_dayend.`fdata_price_dayend`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;

CREATE TABLE finance_fdata_crypto_binance.`fdata_crypto_hist` (
  `ticker` varchar(20) NOT NULL,
  `timeframe` varchar(5) NOT NULL,
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;


ALTER TABLE finance_fdata_crypto_binance.`fdata_crypto_hist`
  ADD PRIMARY KEY (`ticker`,`tDateTime`);
COMMIT;

CREATE TABLE finance_fdata_fut_hist_10secs_2021.`fdata_fut_hist` (
  `ticker` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `instrumenttype` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `timeframe` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE finance_fdata_fut_hist_10secs_2021.`fdata_fut_hist`
  ADD UNIQUE KEY `ticker_key` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`),
  ADD KEY `tick` (`ticker`);
COMMIT;

CREATE TABLE finance_fdata_fut_hist_10secs_2022.`fdata_fut_hist` (
  `ticker` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `instrumenttype` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `timeframe` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE finance_fdata_fut_hist_10secs_2022.`fdata_fut_hist`
  ADD UNIQUE KEY `ticker_key` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`);
COMMIT;


CREATE TABLE finance_fdata_fut_hist_10secs_2023.`fdata_fut_hist` (
  `ticker` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `instrumenttype` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `timeframe` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE finance_fdata_fut_hist_10secs_2023.`fdata_fut_hist`
  ADD UNIQUE KEY `ticker_key` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`);
COMMIT;


CREATE TABLE finance_fdata_price_1min_2020.`fdata_price_1min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_1min_2020.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;

CREATE TABLE finance_fdata_price_1min_2021_h1.`fdata_price_1min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

ALTER TABLE finance_fdata_price_1min_2021_h1.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;


