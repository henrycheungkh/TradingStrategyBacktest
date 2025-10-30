CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_2021;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_2022;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_2023;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_2024;

CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_2020;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_2021_h1;


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

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
  ADD UNIQUE KEY `tickerkey` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
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
  ADD UNIQUE KEY `tickerkey` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
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
  ADD UNIQUE KEY `tickerkey` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`);
COMMIT;

CREATE TABLE finance_fdata_fut_hist_10secs_2024.`fdata_fut_hist` (
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

ALTER TABLE finance_fdata_fut_hist_10secs_2024.`fdata_fut_hist`
  ADD UNIQUE KEY `tickerkey` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
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
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4_0900_ai_ci;

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
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_1min_2021_h1.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;
