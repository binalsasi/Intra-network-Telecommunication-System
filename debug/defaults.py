server_ip = "192.168.50.1";
localhost = "127.0.0.1";
callport = 30020;
commport = 30021;
device_number = '8848';

# URLs
setoffhook_url = "/pythonintercom/device_offhook.php";
callnumber_url = "/pythonintercom/callnumber.php";
callpickedup_url = "/pythonintercom/callpickedup.php";
init_url = "/pythonintercom/init_device.php";

# File Paths
projectdir = "/home/pi/Documents/MiniProject/debug";

path_recordsend = projectdir + "/record_send_udp.py &";
path_receiveplay = projectdir + "/receive_udp_play.py &";
path_playtimeout = projectdir + "/play_tone.py timeout &";
path_playinvalid = projectdir + "/play_tone.py invalid &";
path_playnonexistant = projectdir + "/play_tone.py nonexistant &";
path_playoffline = projectdir + "/play_tone.py offline &";
path_playbusy = projectdir + "/play_tone.py busy &";
path_playringing = projectdir + "/play_tone.py ringing &";
path_hangup = projectdir + "/checkForHangup.py &";
path_convo = projectdir + "/convo.py &";
path_ringphone = projectdir + "/ringphone.py &";
path_playdial = projectdir + "/play_tone.py dial &";
path_dtmf = projectdir + "/dtmf_reader1.py &";
path_inccall = projectdir + "/inccall_handler.py &";
path_offhook = projectdir + "/offhook_detector_1.py &";
path_dtmf_record = projectdir + "/dtmfrecord.py &";


with open('logs/defaults.log', 'w') as log:
    log.write("defaults loaded");
