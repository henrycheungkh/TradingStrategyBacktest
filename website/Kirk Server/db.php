<?php
$servername = "localhost";
$username = "kirklau";
$password = "vytrix123";
$dbname = "sqlsite13";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

?>