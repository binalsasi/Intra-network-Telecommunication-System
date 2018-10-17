#!/usr/bin/python
import time
import socket
import os
import httplib, urllib

import RPi.GPIO as GPIO

# For Pin Definitions
import pins;

# For Shared Memory
import sysv_ipc

# Keys and functions for shared memory
import sharedmem_utils

# Device and server confs
import conf

log = open("logs/dtmf_reader.log", "w", 0);
log.write("dtmf reader was run\n");

# SharedMemory segments
dtmf_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_dtmf);
tone_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_tone);
offhook_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_offhook);
endip_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);

GPIO.setmode(GPIO.BCM)
GPIO.setup(pins.DTMF_INTR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pins.DTMF_BIT0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pins.DTMF_BIT1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pins.DTMF_BIT2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pins.DTMF_BIT3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

digits = []

# Timeout is set for 6 seconds
timeout = int(time.time()) + 20;

dtmfstatus = sharedmem_utils.read_from_memory(dtmf_shm);
#dtmfstatus = 'run';

log.write("started to check for DTMF. initialised sharedmem and pins");

# Check for DTMF until timeout or explicit stop

while int(time.time()) < timeout and dtmfstatus != 'stop':
	# On DTMF input, Interrupt pin will be high for a moment
	# At that moment, save the bit values.
	# If any digit was pressed, the ringing tone stops
	if (GPIO.input(pins.DTMF_INTR) == True):
		digits.append((GPIO.input(pins.DTMF_BIT0),
				GPIO.input(pins.DTMF_BIT1),
				GPIO.input(pins.DTMF_BIT2),
				GPIO.input(pins.DTMF_BIT3)));

		timeout = int(time.time()) + 6;
		sharedmem_utils.write_to_memory(tone_shm, 'stop');
		time.sleep(0.5);
	dtmfstatus = sharedmem_utils.read_from_memory(dtmf_shm);

print (digits)
log.write("digits were obtained as : " + str(digits));

if(dtmfstatus != 'stop'):
	# No number was dialed
	if(len(digits) == 0):
                log.write("no number was dialled");
		# Stop the Dial tone
		sharedmem_utils.write_to_memory(tone_shm, 'stop');
		time.sleep(0.5);
		# Play Timeout Tone
		sharedmem_utils.write_to_memory(tone_shm, 'run');
		os.system(conf.path_playtimeout);
		log.write("stopped dialtone and playing timeout");

	else:
		# Process the bit values to get the number digits
		temp = []
		for (b0,b1,b2,b3) in digits:
                        num = (b0*1 + b1*2 + b2*4 + b3*8);
                        if(num == 10):
                          c = '0'
                        elif num == 11:
                          c = '*'
                        elif num == 12:
                          c = '#';
                        else:
                          c = str(num)
			temp.append(c);
	
		digits = temp;
		print "Digits are : ", str(digits);
		log.write("the digits are : " + str(digits));

if True:
		# Stop Dial tone
		sharedmem_utils.write_to_memory(tone_shm, 'stop');

                digits = ['1','2','3','4'];

		# Send number to server
		params = urllib.urlencode({'device_id': str(conf.device_id), 'callnumber': "".join(digits)})
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

		conn = httplib.HTTPConnection(conf.server_ip)
		conn.request("POST", conf.callnumber_url, params, headers)
		response = conn.getresponse()
		print response.status, response.reason

		# Might be good to check for response status

		# Check Server Reply
		result = response.read();
		log.write("server response : " + str(response.status) + " result : " + str(response.read()))
                print "Server response : ", result

		if result == "number_invalid":
                        print "Result invlid";
                        
			sharedmem_utils.write_to_memory(tone_shm, 'start');
			os.system(conf.path_playinvalid);

		elif result == "number_nonexistant":
                        print "Result nonexist"
			sharedmem_utils.write_to_memory(tone_shm, 'start');
			os.system(conf.path_playinvalid);

		elif result == "number_offline":
                        print "Result off"
			#sharedmem_utils.write_to_memory(tone_shm, 'start');
			#os.system(conf.path_playoffline);

		elif result == "number_busy":
                        print "Result busy"
			#sharedmem_utils.write_to_memory(tone_shm, 'start');
			#os.system(conf.path_playbusy);
		else:
			# If the number was available, get the ip
			print "Result avail"
			
			i = result.find("number_available=");
			if(i != -1):
				endip = result[17:]

				# Start ringing tone
				sharedmem_utils.write_to_memory(tone_shm, 'start');
				os.system(conf.path_playringing);

				# Continuously send udp to the other device until acknowledged
				# Could use TCP as well.
				# Timeout is set for 30 seconds
				ack = False;
				timeout = int(time.time()) + 30;
				offhookstatus = 'offhook'

				# The receiver socket is non-blocking. Which is why 
				# reading the data is checked for exceptions.
				# When there is nothing to read, it raises an exception
				ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				rsock.bind(("192.168.50.2", conf.callport))
				rsock.setblocking(0);

				while not ack and time.time() < timeout and offhookstatus != 'onhook':
                                        print "sending call signal" ,str(ack)
					ssock.sendto("calling", (endip, conf.callport))
					#offhookstatus = sharedmem_utils.read_from_memory(offhook_shm);

					try:
						data, addr = rsock.recvfrom(10);
						print data , " from ", addr

						# Do not acknowledge if the phone is reset to onhook. This way
						# the other device will also stop trying to establish connection
						if data == "ack" and str(addr[0]) == endip :#and offhookstatus != 'onhook':
                                                        print "sending ackack"
							ssock.sendto("ackack", (endip, conf.callport));
							ack = True;
					except socket.error:
						"do nothing"
					time.sleep(1);

				ssock.close()
				rsock.close()

				# if acknowledged, stop ringing tone,
				# start checking for hangup
				# start recording, sending, receiving and playing of audio
				if ack:
                                        print "ack. start conv"
					sharedmem_utils.write_to_memory(endip_shm, endip);

					sharedmem_utils.write_to_memory(tone_shm, 'stop');

					#os.system(conf.path_hangup);

					sharedmem_utils.write_to_memory(convo_shm, 'start');
					#os.system(conf.path_convo);
				else:
                                        print "no ack. timeout. "
					# Timeout occured.
					if(offhookstatus != 'onhook'):
						# Stop Ringing tone and start timeout tone
						sharedmem_utils.write_to_memory(tone_shm, 'stop');
						time.sleep(0.5);
						sharedmem_utils.write_to_memory(tone.shm, 'start');
						#os.system(conf.path_playtimeout);
			else:
				print "Unknown response : ", result;
			
		#stop listening to dtmf
