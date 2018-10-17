#!/usr/bin/python2
# For UDP
import socket

# For SharedMemory
import sysv_ipc

# For Keys and functions for shared memory
import sharedmem_utils

# For Device and Server confs
import conf

# SharedMemory segments
offhook_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_offhook)
endip_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);

# The values (statuses) in the shared memory segments
endip = sharedmem_utils.read_from_memory(endip_shm);
offhookstatus = sharedmem_utils.read_from_memory(offhook_shm);

# Create a UDP socket that is non-blocking, waiting for the hangup message
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind((conf.localhost, conf.callport))
sock.setblocking(0);

hangup = False;

# Wait for hangup, until hungup or phone is replaced on hook
while hangup != True and offhookstatus != 'onhook':
	offhookstatus = sharedmem_utils.read_from_memory(offhook_shm);
	try:
		data, addr = sock.recvfrom(10)
		print "received message:", data
		if data == "hangup" and str(addr) == endip:
			hangup = True;
			sharedmem_utils.write_to_memory(convo_shm, 'stop');

	except socket.error:
		"do nothing"

sock.close();
