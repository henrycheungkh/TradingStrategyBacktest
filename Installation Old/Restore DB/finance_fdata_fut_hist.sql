-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 19, 2021 at 05:00 PM
-- Server version: 10.4.13-MariaDB
-- PHP Version: 7.4.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `finance_fdata_fut_hist`
--

-- --------------------------------------------------------

--
-- Table structure for table `fdata_fut_hist`
--

CREATE TABLE `fdata_fut_hist` (
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

--
-- Indexes for dumped tables
--

--
-- Indexes for table `fdata_fut_hist`
--
ALTER TABLE `fdata_fut_hist`
  ADD UNIQUE KEY `ticker` (`ticker`,`DataType`,`expiry`,`tDateTime`,`timeframe`,`instrumenttype`) USING BTREE,
  ADD KEY `tDateTime` (`tDateTime`),
  ADD KEY `tick` (`ticker`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
