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

require_once('includes/cardinalconfig.php');

// Form for the deletion of 2.4GHz SSIDs

$ssid24Result = $conn->query("select ap_ssid_id,ap_ssid_name from ssids_24ghz_radius");

echo "<html>\n";
echo "<head>\n";
echo "</head>\n";
echo "<body>\n";
echo "<font face=\"Verdana\">\n";
echo "Choose 2.4GHz RADIUS SSID:";
echo "<br>";
echo "<br>";
echo "</font>";
echo "<form id=\"delete_ssid_24ghz_data\" action=\"\" method=\"POST\">\n";
echo "<select name='ssid24id'>";

    while ($ssid24Row = $ssid24Result->fetch_assoc()) {

                  unset($ssid24Id, $ssid24name);
                  $ssid24Id = $ssid24Row['ap_ssid_id'];
                  $ssid24name = $ssid24Row['ap_ssid_name'];
                  echo '<option value="'.$ssid24Id.'">'.$ssid24name.'</option>';
 
}

echo "</select>";
echo "<input type=\"button\" value=\"Delete 2.4GHz RADIUS SSID\" name=\"delete_ssid_24ghz_mysql\" onclick=\"askForSsid24Delete()\" />\n";
echo "</form>\n";
echo "<script>\n";
echo "form=document.getElementById(\"delete_ssid_24ghz_data\");\n";
echo "function askForSsid24Delete() {\n";
echo "        form.action=\"delete_ssid_db_24ghz_radius.php\";\n";
echo "        form.submit();\n";
echo "}\n";

echo "</script>\n";
echo "</body>\n";
echo "</html>";


$conn->close();

?>

<button onclick="window.location.href='/delete_ssid_wizard.php'">Back to Delete SSID Wizard</button>
