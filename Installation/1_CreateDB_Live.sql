CREATE DATABASE IF NOT EXISTS finance_fdata_master;

CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_10secs;
CREATE DATABASE IF NOT EXISTS finance_fdata_fut_hist_5secs;

CREATE DATABASE IF NOT EXISTS finance_fdata_price_30min_ib;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_ib;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_dayend_ib;

CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min_fx;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_1min;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_2min_fx;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_2min;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_30min;
CREATE DATABASE IF NOT EXISTS finance_fdata_price_dayend;

CREATE DATABASE IF NOT EXISTS finance_fdata_crypto_binance;


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

COMMIT;

# ALTER TABLE finance_fdata_master.pending_db_upload_command
# ADD COLUMN DBSuffix VARCHAR(10) DEFAULT '';


# Convert an entire table
# ALTER TABLE fdata_tickers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

# Or just the column (preserve the right length)
# ALTER TABLE fdata_tickers
  MODIFY ticker VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS finance_fdata_fut_hist.`fdata_fut_hist` (
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


CREATE TABLE IF NOT EXISTS finance_fdata_fut_hist_10secs.`fdata_fut_hist` (
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


CREATE TABLE IF NOT EXISTS finance_fdata_fut_hist_5secs.`fdata_fut_hist` (
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
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_1min_ib.`fdata_price_1min_ib`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;

CREATE TABLE finance_fdata_price_dayend_ib.`fdata_price_dayend_ib` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_dayend_ib.`fdata_price_dayend_ib`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;

CREATE TABLE finance_fdata_price_dayend_ib.`fdata_price_dayend_ib_adjusted` (
  `ticker` varchar(20) NOT NULL,
  `DataType` varchar(6) NOT NULL,
  `timeframe` varchar(10) NOT NULL,
  `DateTime` datetime NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `open` double NOT NULL,
  `close` double NOT NULL,
  `vol` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_dayend_ib.`fdata_price_dayend_ib_adjusted`
  ADD PRIMARY KEY (`ticker`,`DateTime`,`DataType`,`timeframe`) USING BTREE;
COMMIT;

CREATE TABLE finance_fdata_price_dayend_ib.`fdata_finsummary_dividend` (
  `ticker` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `exDate` date NOT NULL,
  `recordDate` date NOT NULL,
  `payDate` date NOT NULL,
  `declarationDate` date NOT NULL,
  `value` double NOT NULL,
  PRIMARY KEY (`ticker`,`type`,`exDate`,`recordDate`,`payDate`,`declarationDate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE finance_fdata_price_dayend_ib.`fdata_finsummary_divpershare` (
  `ticker` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `asofDate` date NOT NULL,
  `reportType` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `period` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `value` double NOT NULL,
  PRIMARY KEY (`ticker`,`asofDate`,`reportType`,`period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE finance_fdata_price_1min_fx.`fdata_price_1min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_1min_fx.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
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
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_1min.`fdata_price_1min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;



CREATE TABLE finance_fdata_price_2min_fx.`fdata_price_2min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_2min_fx.`fdata_price_2min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
COMMIT;



CREATE TABLE finance_fdata_price_2min.`fdata_price_2min` (
  `ticker` varchar(20) NOT NULL,
  `Datetime` datetime NOT NULL,
  `Adj Close` double NOT NULL,
  `Close` double NOT NULL,
  `High` double NOT NULL,
  `Low` double NOT NULL,
  `Open` double NOT NULL,
  `Volume` double NOT NULL
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_2min.`fdata_price_2min`
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
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

ALTER TABLE finance_fdata_price_30min.`fdata_price_30min`
  ADD PRIMARY KEY (`ticker`,`Datetime`);
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
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

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
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;


ALTER TABLE finance_fdata_crypto_binance.`fdata_crypto_hist`
  ADD PRIMARY KEY (`ticker`,`tDateTime`);
COMMIT;


