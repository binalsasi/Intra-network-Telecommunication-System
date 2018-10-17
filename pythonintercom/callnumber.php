<?php
	if($_POST){
		$device_id = $_POST['device_id'];
		$callnumber = $_POST['callnumber'];

		$conn = mysql_connect("localhost", "miniuser", "12345678");
		mysql_select_db("Miniproject");

		$ret = mysql_query("select * from Devices where Number = '$callnumber'", $conn);
		if(!$ret){
			echo "ERROR".mysql_error();
		}
		else{
			if(mysql_num_rows($ret) != 0){
				$arr = mysql_fetch_assoc($ret);
				if($arr['Status'] === "available"){
					echo "number_available=${arr['IP_Address']}";
					$ret = mysql_query("update Devices set endip ='$callnumber' where DeviceID='$device_id'");
				}
				elseif($arr['Status'] == "busy"){
					echo "number_busy";
				} 
			}
			else{
				echo "number_nonexistant";
			}
		}
		mysql_close($conn);
	}
?>
