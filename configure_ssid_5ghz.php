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

?>

<html>
<form id="add_5ghz_ssid" action="functions/configure_ssid_5ghz_calc.php" method="POST">
<font face="Verdana">
<label>SSID Name: </label>
<input type="text" name="ssid_name" required>
<br>
<label>WPA2-PSK (Minimum 8 Characters): </label>
<input type="password" name="wpa2_psk" required>
<br>
<label>VLAN: </label>
<input type="text" name="vlan" required>
<br>
<label>Bridge Group ID: </label>
<input type="text" name="bridge_group_id" required>
<br>
<label>5GHz Radio Sub Interface ID: </label>
<input type="text" name="5_sub_id" required>
<br>
<label>Gigabit Sub Interface ID: </label>
<input type="text" name="giga_sub_id" required>
<br>
<input type="submit" name="Submit" required>
</font>
</form>
</html>

<button onclick="window.location.href='/configure_ssid_wizard.php'">Back to Configure SSID Wizard</button>

<?php

// Success after SSID registration (from configure_ssid_5ghz_calc.php)
if ( isset($_GET['Success']) && $_GET['Success'] == 1 )
{
     // Success Message!
     echo "<br>";
     echo "<br>";
     ?>
     <font face="Verdana">
     <?php echo "5GHz SSID Created Successfully!"; ?>
     </font>
<?php } ?>

<?php

$conn->close();

?>

