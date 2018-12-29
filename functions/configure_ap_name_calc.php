<?php

/* Cardinal - An Open Source Cisco Wireless Access Point Controller

MIT License

Copyright © 2017 falcon78921

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/

// Cardinal Login Session

session_start();

// If user is not logged into Cardinal, then redirect them to the login page

if (!isset($_SESSION['username'])) {
header('Location: index.php');
}

// MySQL connection information

require_once(__DIR__ . '/../includes/cardinalconfig.php');

// Fetch AP Session

$varAPId = $_SESSION['apid'];

$sql = "SELECT ap_ip,ap_ssh_username,ap_ssh_password FROM access_points WHERE ap_id = $varAPId";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // store data of each row
    while($row = $result->fetch_assoc()) {
       $queryIP = $row["ap_ip"];
       $queryUser = $row["ap_ssh_username"];
       $queryPass = $row["ap_ssh_password"];
       $queryApName = $_POST["ap_name"];
       $pyCommand = escapeshellcmd("scout --change-name $queryIP $queryUser $queryPass $queryApName");
       $pyOutput = shell_exec($pyCommand);
       $phpMySQLUpdate = "UPDATE access_points SET ap_name = '$queryApName' WHERE ap_ip = '$queryIP'";
       $phpMySQLQuery = mysqli_query($conn,$phpMySQLUpdate);
       $phpMySQLValue = mysqli_fetch_object($phpMySQLQuery);
       // Redirect with success message.
       header('Location: ../configure_ap_name.php?Success=1');
     }
} else {
    echo "";
}

$conn->close();

?>
