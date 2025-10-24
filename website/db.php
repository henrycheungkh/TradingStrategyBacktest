<?php
$servername = "localhost";
$username = "id17266298_stockfry";
$password = "%\TO(6M}SHh]/E}?";
$dbname = "id17266298_finance";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

?>