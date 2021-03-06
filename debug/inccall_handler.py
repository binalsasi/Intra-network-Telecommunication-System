#!/usr/bin/python
import socket
import conf
import sysv_ipc
import sharedmem_utils
import httplib, urllib
from time import sleep

log = open("logs/inccall.log", "w", 0);
log.write("inccall handler has started\n");

inccall_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_inccall);
inccallstatus = sharedmem_utils.read_from_memory(inccall_shm);

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

endip_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);
calls_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_calls);
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
#ringphone_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_ringphone);

rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rsock.bind((conf.localhost, conf.callport))
rsock.setblocking(0)

log.write("declared all variables\n");
log.write("starting loop now\n");

while inccallstatus != 'stop':
	try:
		data, addr = rsock.recvfrom(10);
		if(data == 'calling'):
			log.write("incoming call" + str(addr) + "\n");
			# Ring the phone
			# sharedmem_utils.write_to_memory(ringphone_shm, 'start');
			# os.system(conf.path_ringphone);
			print "Address ", addr, " is calling";
			sharedmem_utils.write_to_memory(calls_shm, 'calling');
			sharedmem_utils.write_to_memory(endip_shm, addr);

		elif(data == 'hangup'):
                        sharedmem_utils.write_to_memory(convo_shm, 'stop');
	except socket.error:
		"do nothing"
	inccallstatus = sharedmem_utils.read_from_memory(inccall_shm);
	sleep(1);

log.write("sending ack\n");

# The phone is off hook at this point
# Stop ringing the phone
#sharedmem_utils.write_to_memory(ringphone_shm, 'stop');

# Send pickup acknowledgement to the other end
ssock.sendto("ack", (endip, conf.callport))
rsock.setblocking(1);

# Wait for acknowledgement
data, addr = rsock.recvfrom(10);
if(data == "ackack"):
	# Notify server that call has been picked up
	log.write("ackack obtained\n")
	params = urllib.urlencode({'device_id': conf.device_id, 'call': 'pickedup', 'endip' : endip})
	conn = httplib.HTTPConnection(conf.server_ip)
	conn.request("POST", conf.callpickedup_url, params, headers)
	response = conn.getresponse()
	print response.status, response.reason

	# Start conversation
	sharedmem_write_to_memory(convo_shm, 'start');
	os.system(conf.path_convo);

	# Start listen for hangup
	os.system(conf.path_hangup);
