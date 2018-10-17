import sys
import time
import socket
import os
import httplib, urllib


# For Shared Memory
import sysv_ipc

# Keys and functions for shared memory
import sharedmem_utils

# Device and server confs
import conf

dtmf_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_dtmf);
tone_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_tone);
offhook_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_offhook);
endip_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);



if len(sys.argv) != 2:
	print "Must give number as argument!"

else:
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
	num = sys.argv[1];

	params = urllib.urlencode({'device_id': str(conf.device_id), 'callnumber': num})
	headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

	conn = httplib.HTTPConnection(conf.server_ip)
	conn.request("POST", conf.callnumber_url, params, headers)
	response = conn.getresponse()
	print response.status, response.reason

	# Might be good to check for response status

	# Check Server Reply
	result = response.read();

	i = result.find("number_available=");
	if(i != -1):
		endip = result[17:]


		# Continuously send udp to the other device until acknowledged
		# Could use TCP as well.
		# Timeout is set for 30 seconds

		ack = False;
		timeout = int(time.time()) + 30;
		offhookstatus = sharedmem_utils.read_from_memory(offhook_shm);

		# The receiver socket is non-blocking. Which is why 
		# reading the data is checked for exceptions.
		# When there is nothing to read, it raises an exception
		ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		rsock.bind((conf.localhost, conf.callport))
		rsock.setblocking(0);

		while not ack and time.time() < timeout and offhookstatus != 'onhook':
			print "sending call signal to ", endip, " ack = " ,str(ack)
			ssock.sendto("calling", (endip, conf.callport))
			offhookstatus = sharedmem_utils.read_from_memory(offhook_shm);
			if(offhookstatus == "onhook" and  time.time() < timeout):
				ssock.sendto("cancel", (endip, conf.callport));
				print "Onhook before call ack";
				break;
			try:
				data, addr = rsock.recvfrom(10);
				print data , " from ", addr

				# Do not acknowledge if the phone is reset to onhook. This way
				# the other device will also stop trying to establish connection
				if data == "ack" and str(addr[0]) == endip and offhookstatus != 'onhook':
					print "sending ackack"
					ssock.sendto("ackack", (endip, conf.callport));
					ack = True;
			except socket.error:
				"do nothing"
			time.sleep(1);

		# ssock.close()
		rsock.close()

		# if acknowledged, stop ringing tone,
		# start checking for hangup
		# start recording, sending, receiving and playing of audio
		if ack:
			print "ack. start conv"
			sharedmem_utils.write_to_memory(endip_shm, endip);
			sharedmem_utils.write_to_memory(tone_shm, 'stop');
			os.system(conf.path_hangup);

			sharedmem_utils.write_to_memory(convo_shm, 'start');
			os.system(conf.path_convo2);
		else:
			print "no ack. timeout. "
			# Timeout occured.
			if(offhookstatus != 'onhook'):
				# Stop Ringing tone and start timeout tone
				sharedmem_utils.write_to_memory(tone_shm, 'stop');
				time.sleep(0.5);
				sharedmem_utils.write_to_memory(tone_shm, 'start');
				os.system(conf.path_playtimeout);

				ssock.sendto("cancel", (endip, conf.callport));

		ssock.close();

