<html>
<head>
<title>Gapper Update</title>
</head>
<body>
Gapper Update<BR><BR>


<?php 
error_reporting(E_ALL);
include 'db.php';

?>

<?php

// https://www.vytrix.com/stockfry/gapper_update.php?Delete=Yes&CaptureDate=20211029&Ticker1=AAPL&Sector1=NA&Industry1=NA&PriorDayClose1=200&CurrentPrice1=0&MA30Vol1=10000&TodayVol1=25000&MarketCap1=1200000000&FreeFloat1=240000&BidAskSpread1=0.05&Ticker2=MSFT&Sector2=NA&Industry2=NA&PriorDayClose2=250&CurrentPrice2=0&MA30Vol2=10000&TodayVol2=25000&MarketCap2=1200000000&FreeFloat2=240000&BidAskSpread2=0.05
// https://www.vytrix.com/stockfry/gapper_update.php?Delete=No&CaptureDate=20211029&Ticker1=AAPL&Sector1=NA&Industry1=NA&PriorDayClose1=200&CurrentPrice1=0&MA30Vol1=10000&TodayVol1=25000&MarketCap1=1200000000&FreeFloat1=240000&BidAskSpread1=0.05&Ticker2=MSFT&Sector2=NA&Industry2=NA&PriorDayClose2=250&CurrentPrice2=0&MA30Vol2=10000&TodayVol2=25000&MarketCap2=1200000000&FreeFloat2=240000&BidAskSpread2=0.05

$x = 1;

if (isset($_GET['Delete'])) {
  mysqli_autocommit($conn, FALSE);
  if ($_GET['Delete'] == 'Yes') {
      mysqli_query($conn, "DELETE FROM finance_fdata_us_gapper_list where CaptureDate = '" . $_GET['CaptureDate'] . "'");
  }
  
  while(isset($_GET['Ticker'.$x])) {
    echo $_GET['Ticker'.$x] . '<BR>';
    mysqli_query($conn, "INSERT INTO finance_fdata_us_gapper_list VALUES ('". $_GET['CaptureDate'] . "', '" . $_GET['Ticker'.$x] . "', '" . $_GET['Sector'.$x] . "', '" . $_GET['Industry'.$x] . "', " . $_GET['PriorDayClose'.$x] . ", " . $_GET['CurrentPrice'.$x] . ", " . $_GET['MA30Vol'.$x] . ", " . $_GET['TodayVol'.$x] . ", " . $_GET['MarketCap'.$x] . ", " . $_GET['FreeFloat'.$x]. ", " . $_GET['BidAskSpread'.$x] . ", NULL, NULL)");
    $x++;
  }
  mysqli_commit($conn);
}
?>

</body>
</html>