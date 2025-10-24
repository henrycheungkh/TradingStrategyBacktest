-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 02, 2025 at 09:37 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `finance_fdata_fut_hist_5secs`
--

-- --------------------------------------------------------

--
-- Table structure for table `fdata_fut_hist`
--

CREATE TABLE IF NOT EXISTS `fdata_fut_hist` (
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

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
