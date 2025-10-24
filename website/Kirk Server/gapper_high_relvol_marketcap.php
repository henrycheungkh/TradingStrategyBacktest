<html>
<head>
<title>Gapper</title>
<meta http-equiv="refresh" content="5" >
</head>
<body>
Gapper<BR><BR>
Relative Vol > 3, Market Cap > 100mm, Price Gap > 4%, Dollar Volume > $50,000<BR><BR>

<?php include 'db.php';?>
<?php

echo "The time is " . date("h:i:sa") . "<BR>";
$date = new DateTime("now", new DateTimeZone('America/New_York') );
echo "The New York time is " . $date->format('Y-m-d H:i:s'). "<BR><BR>";

$sql = "SELECT *, (CurrentPrice - PriorDayClose)/PriorDayClose AS GapSize, Today_Vol/(30MA_Vol+0.001) AS RelativeVol FROM finance_fdata_us_gapper_list WHERE Today_Vol/30MA_Vol > 3 AND MarketCap > 100000000 AND ABS((CurrentPrice - PriorDayClose)/PriorDayClose) > 0.04 AND CaptureDate = '" . $date->format('Y-m-d') . "' ORDER BY ABS((CurrentPrice - PriorDayClose)/PriorDayClose) DESC";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
  // output data of each row

  echo "<table border=1 style=\"text-align:center\"><tr><th>Capture Date</th><th>Gap Size %</th><th>Ticker</th><th>Prior Day Close</th><th>Current Price</th><th>Relative Vol %</th><th>30MA Vol</th><th>Today Vol</th><th>Market Cap</th><th>Free Float</th><th>Bid Ask Spread to Spot %</th><th>Sector</th><th>Industry</th></tr>";
  while($row = $result->fetch_assoc()) {
    echo "<tr><td>" . $row["CaptureDate"]. "</td><td>" . round($row["GapSize"]*100,2). "</td><td>" . $row["ticker"]. "</td><td>" . $row["PriorDayClose"]. "</td><td>" . $row["CurrentPrice"]. "</td><td>" . round($row["RelativeVol"]*100, 2). "</td><td>" . number_format($row["30MA_Vol"]). "</td><td>" . number_format($row["Today_Vol"]). "</td><td>" . number_format($row["MarketCap"]). "</td><td>" . number_format($row["FreeFloat"]). "</td><td>" . round($row["BidAskSpread"] * 100, 2). "</td><td>" . $row["Sector"]. "</td><td>" . $row["Industry"]. "</td></tr>";
  }

  echo "</table>";
} else {
  echo "No results";
}

?>

</body>
</html>