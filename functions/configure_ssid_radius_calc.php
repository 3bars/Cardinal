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
header('Location: ../../index.php');
}

// Cardinal Configuration Information

require_once(__DIR__ . '/../includes/cardinalconfig.php');

// MySQL connection information

require_once(__DIR__ . '/../includes/cardinalconfig.php');

// Declare POST variables

$querySSID = $_POST['ssid_name'];
$queryVlan = $_POST['vlan'];
$queryBridgeGroup = $_POST['bridge_group_id'];
$queryRadioSub = $_POST['24_sub_id'];
$queryGigaSub = $_POST['giga_sub_id'];
$queryRadiusIP = $_POST['radius_ip'];
$querySharedSecret = $_POST['shared_secret'];
$queryAuthPort = $_POST['auth_port'];
$queryAcctPort = $_POST['acct_port'];
$queryRadiusTimeout = $_POST['radius_timeout'];
$queryRadiusGroup = $_POST['radius_group'];
$queryMethodList = $_POST['method_list'];

// Store SSID Data in Database 
if ($_POST) {
$ssidUpdate = "INSERT INTO ssids_24ghz_radius (ap_ssid_name, ap_ssid_vlan, ap_ssid_bridge_id, ap_ssid_radio_id, ap_ssid_ethernet_id, ap_ssid_radius_server, ap_ssid_radius_secret, ap_ssid_authorization_port, ap_ssid_accounting_port, ap_ssid_radius_timeout, ap_ssid_radius_group, ap_ssid_radius_method_list) VALUES ('$querySSID', '$queryVlan', '$queryBridgeGroup', '$queryRadioSub', '$queryGigaSub', '$queryRadiusIP', '$querySharedSecret', '$queryAuthPort', '$queryAcctPort', '$queryRadiusTimeout', '$queryRadiusGroup', '$queryMethodList')";
$ssidQuery = mysqli_query($conn,$ssidUpdate);
$ssidValue = mysqli_fetch_object($ssidQuery);
// Redirect to this page.
header('Location: ../configure_ssid_radius.php?Success=1');
exit();
}

// Clear POST Variables
unset($_POST);

// Close SQL connection

$conn->close();

?>
