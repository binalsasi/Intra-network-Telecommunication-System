#!/usr/bin/python2

## TODO we can check for offhook status as condition for start and stop, instead of seperate state variables

from time import sleep
import os
import httplib, urllib
import socket

# For shared memory
import sysv_ipc

# Keys and functions for shared memory
import sharedmem_utils

# Device and Server Confs
import conf


log = open("logs/offhook.log", "w", 0);
log.write("offhook is started\n");


# Encode and save POST data that is used to notify the server
offhookparams = urllib.urlencode({'device_id': conf.device_id, 'hookstatus': 'offhook'})
onhookparams = urllib.urlencode({'device_id': conf.device_id, 'hookstatus': 'onhook'})
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

# SharedMemory segments
offhook_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_offhook);
inccall_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_inccall);
tone_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_tone);
dtmf_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_dtmf);
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
calls_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_calls);
endip_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);

# SharedMemory Control. Statuses.
# Some of these are not needed.
offhookstatus = sharedmem_utils.read_from_memory(offhook_shm);
inccallstatus = sharedmem_utils.read_from_memory(inccall_shm);
tonestatus = sharedmem_utils.read_from_memory(tone_shm);
dtmfstatus = sharedmem_utils.read_from_memory(dtmf_shm);
callsstatus = sharedmem_utils.read_from_memory(calls_shm);
endip = sharedmem_utils.read_from_memory(endip_shm);

log.write("offhook has declared all variables\n");
log.write("offhook is entering loop\n");

offcount = 0
oncount = 0


phone_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_phone);

while True:
	# Only perform the actions once, hence the offhookstatus
	phone_status = sharedmem_utils.read_from_memory(phone_shm);
	if (phone_status == "offhook"):
                print "here"
                offcount += 1
                oncount = 0
                if (offhookstatus != 'offhook' and offcount > 1):
                        log.write("phone is now offhook\n");
                        print "phone is off hook";
                        # Phone has become off hook
                        sharedmem_utils.write_to_memory(offhook_shm, 'offhook');
                        offhookstatus = 'offhook';

                        # Notify the server that the phone has become off hook
                        conn = httplib.HTTPConnection(conf.server_ip)
                        conn.request("POST", conf.setoffhook_url, offhookparams, headers)
                        response = conn.getresponse()
                        print response.status, response.reason

                        # Stop checking for incoming calls.
                        # The status will be changed to wait, when dialing is complete
                        sharedmem_utils.write_to_memory(inccall_shm, 'stop');

                	callsstatus = sharedmem_utils.read_from_memory(calls_shm);
                        if(callsstatus != 'calling'):
                                log.write("no incoming call. dial ops\n");
                                # Play dialtone
                                #store file paths in a py. and use it
                                #sharedmem_utils.write_to_memory(tone_shm, 'run');
                                #tonestatus = "run";
                                #os.system(conf.path_playdial);

                                # Listen to DTMF values
                                sharedmem_utils.write_to_memory(dtmf_shm, 'run');
#                                os.system(conf.path_dtmf_record);


	else:
                oncount += 1
                offcount = 0
		if(offhookstatus != 'onhook' and oncount > 5):
                        #offcount = 0
			log.write("phone is now on hook\n");
                        print "phone is on hook";
			# Phone has returned On Hook
			# Actions depending on the hook status would read the shared memory 
			# segment to see that it has become on hook
			sharedmem_utils.write_to_memory(offhook_shm, 'onhook');
			offhookstatus = 'onhook';

			# Stop playing any tones
			tonestatus = 'stop'
			sharedmem_utils.write_to_memory(tone_shm, 'stop');

			# Stop listening to DTMF
			sharedmem_utils.write_to_memory(dtmf_shm, 'stop');

			# Stop waiting for hangup
			# Hangup checks on the status of offhook itself.

			# Stop sending and receiving audio
			convostatus = sharedmem_utils.read_from_memory(convo_shm);
			sharedmem_utils.write_to_memory(convo_shm, 'stop');
			# If was in conversation, when onhook occurs, send 'hangup' message to the other device
			if convostatus == 'start':
				log.write("hanging up conversation\n");
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				endip = sharedmem_utils.read_from_memory(endip_shm);
				sock.sendto("hangup", (endip, conf.callport))
				sock.close()


			callsstatus = sharedmem_utils.read_from_memory(calls_shm);
			if(callsstatus == 'calling'):
				log.write("resetting incoming call status\n");
				sharedmem_utils.write_to_memory(calls_shm, 'nocalls');
				callsstatus = "nocalls";


			# Start checking for incoming calls
			sharedmem_utils.write_to_memory(inccall_shm, 'run');
#			os.system(conf.path_inccall);

			# Notify the server that the phone has become on hook
			conn = httplib.HTTPConnection(conf.server_ip)
			conn.request("POST", conf.setoffhook_url, onhookparams, headers)
			response = conn.getresponse()
			print response.status, response.reason

	# Sleep for half a second
	sleep(0.4);
