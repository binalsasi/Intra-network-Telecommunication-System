<?php
	if($_POST){
		$device_id = $_POST['device_id'];
		$hookstatus = $_POST['hookstatus'];

		$conn = mysql_connect("localhost", "miniuser", "12345678");
		mysql_select_db("Miniproject");

		if($hookstatus == "offhook"){
			$ret = mysql_query("update Devices set Status = 'busy' where DeviceID = $device_id", $conn);
		}
		elseif($hookstatus == "onhook"){
			$ret = mysql_query("update Devices set Endip = '', Status = 'available' where DeviceID = $device_id", $conn);
		}
		else
			$ret = false;
		if(!$ret){
			echo "ERROR". mysql_error();
		}
		else{
			echo "okay";
		}
		mysql_close($conn);
	}
?>
