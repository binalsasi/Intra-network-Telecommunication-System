<?php
	if($_POST){
		$device_id = $_POST['device_id'];
		$endip = $_POST['endip'];
		$call = $_POST['call'];

		$conn = mysql_connect("localhost", "miniuser", "12345678");
		mysql_select_db("Miniproject");

		$ret = mysql_query("update Devices set Endip = '$endip', Status = 'busy' where DeviceID = $device_id", $conn);
		if(!$ret){
			echo "ERROR".mysql_error();
		}
		else{
			echo "okay";
		}
		mysql_close($conn);
	}
?>
