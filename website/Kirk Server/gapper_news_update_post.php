<html>
<head>
<title>Gapper News Update</title>
</head>
<body>
Gapper News Update<BR><BR>


<?php include 'db.php';?>

<?php

// https://stockfry.000webhostapp.com/gapper_update.php?CaptureDate=20210718&Ticker1=AAPL&Sector1=NA&Industry1=NA&PriorDayClose1=200&CurrentPrice1=0&MA30Vol1=10000&TodayVol1=25000&MarketCap1=1200000000&FreeFloat1=240000&BidAskSpread1=0.05&Ticker2=MSFT&Sector2=NA&Industry2=NA&PriorDayClose2=250&CurrentPrice2=0&MA30Vol2=10000&TodayVol2=25000&MarketCap2=1200000000&FreeFloat2=240000&BidAskSpread2=0.05

$x = 1;

if (isset($_POST['CaptureDate'])) {
  mysqli_autocommit($conn, FALSE);
 
  while(isset($_POST['Ticker'.$x])) {
    echo $_POST['Ticker'.$x] . '<BR>';
    mysqli_query($conn, "INSERT INTO finance_fdata_us_gapper_list_news VALUES ('" . $_POST['CaptureDate'] . "', '" . $_POST['Ticker'.$x] . "', '" . $_POST['title'.$x] . "', '" . $_POST['media'.$x] . "', '" . $_POST['date_desc'.$x] . "', '" . $_POST['datetime'.$x] . "', '" . $_POST['news_desc'.$x] . "', '" . $_POST['link_desc'.$x] . "' ) ON DUPLICATE KEY UPDATE media = '" . $_POST['media'.$x] . "'");
    $x++;
  }
  mysqli_commit($conn);
}
?>

</body>
</html>