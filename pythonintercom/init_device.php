<?php
	if($_POST){
		$number = $_POST['auth'];

		$conn = mysql_connect("localhost", "miniuser", "12345678") or die(mysql_error());
		mysql_select_db("Miniproject");

		$ret = mysql_query("select * from Devices where Number = '$number'", $conn);
		if(!$ret){
			echo "ERROR : " .mysql_error();
		}
		else{
			if(mysql_num_rows($ret) == 0){
				$ret = mysql_query("insert into Devices (Number, IP_Address) values ('$number', '${_SERVER['REMOTE_ADDR']}')", $conn);
				if(!$ret){
					echo "ERROR : " . mysql_error();
				}
			}

			$ret = mysql_query("select DeviceID from Devices where Number = '$number'", $conn);
			$ret = mysql_fetch_assoc($ret);
			echo "device_id=".$ret['DeviceID'];
		}
		mysql_close($conn);
	}
?>
