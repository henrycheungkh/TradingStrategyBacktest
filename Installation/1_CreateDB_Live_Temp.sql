CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_temp;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs_temp;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_5secs_temp;

CREATE DATABASE IF NOT EXISTS finance_fdata_price_30min_ib_temp;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_ib_temp;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_dayend_ib_temp;



SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

COMMIT;

CREATE TABLE IF NOT EXISTS finance_fdata_fut_hist_temp.`fdata_fut_hist` (
  `ticker` varchar(10) NOT NULL,
  `instrumenttype` varchar(10) NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) NOT NULL,
  UNIQUE KEY `tickerkey` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  KEY `tDateTime` (`tDateTime`),
  KEY `tick` (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
COMMIT;


CREATE TABLE IF NOT EXISTS finance_fdata_fut_hist_10secs_temp.`fdata_fut_hist` (
  `ticker` varchar(10) NOT NULL,
  `instrumenttype` varchar(10) NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) NOT NULL,
  UNIQUE KEY `tickerkey` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  KEY `tDateTime` (`tDateTime`),
  KEY `tick` (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
COMMIT;


CREATE TABLE IF NOT EXISTS finance_fdata_fut_hist_5secs_temp.`fdata_fut_hist` (
  `ticker` varchar(10) NOT NULL,
  `instrumenttype` varchar(10) NOT NULL,
  `expiry` mediumint(9) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL DEFAULT '',
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL,
  `src` varchar(15) NOT NULL,
  UNIQUE KEY `tickerkey` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  KEY `tDateTime` (`tDateTime`),
  KEY `tick` (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
COMMIT;


CREATE TABLE finance_fdata_price_30min_ib_temp.`fdata_price_30min_ib` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_30min_ib_temp.`fdata_price_30min_ib`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;

CREATE TABLE finance_fdata_price_1min_ib_temp.`fdata_price_1min_ib` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_1min_ib_temp.`fdata_price_1min_ib`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;

CREATE TABLE finance_fdata_price_dayend_ib_temp.`fdata_price_dayend_ib` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_dayend_ib_temp.`fdata_price_dayend_ib`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;

CREATE TABLE finance_fdata_price_dayend_ib_temp.`fdata_price_dayend_ib_adjusted` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_dayend_ib_temp.`fdata_price_dayend_ib_adjusted`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;


CREATE TABLE finance_fdata_price_1min_fx_temp.`fdata_price_1min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_1min_fx_temp.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;



CREATE TABLE finance_fdata_price_1min_temp.`fdata_price_1min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_1min_temp.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;

CREATE TABLE finance_fdata_price_30min_temp.`fdata_price_30min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_30min_temp.`fdata_price_30min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;



CREATE TABLE finance_fdata_price_dayend_temp.`fdata_price_dayend` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` date NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_dayend_temp.`fdata_price_dayend`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;




CREATE TABLE finance_fdata_crypto_binance_temp.`fdata_crypto_hist` (
  `ticker` varchar(20) NOT NULL,
  `timeframe` varchar(5) NOT NULL,
  `tDateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4_0900_ai_ci;


ALTER TABLE finance_fdata_crypto_binance_temp.`fdata_crypto_hist`
  ADD PRIMARY KEY (`ticker`,`tDateTime`);
COMMIT;


