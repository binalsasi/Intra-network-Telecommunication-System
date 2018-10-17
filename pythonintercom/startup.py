#!/usr/bin/python2
import os
import httplib, urllib

# defaults.py contains the default values such as server ip, urls, etc
import defaults

# For SharedMemory functions
import sysv_ipc
import sharedmem_utils

# Data to be sent to server, for setup
params = urllib.urlencode({'auth': 'project#1'})
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

# Send auth, and receive device id
#conn = httplib.HTTPConnection(defaults.server_ip)
#conn.request("POST", defaults.init_url, params, headers)

#response = conn.getresponse()
#print response.status, response.reason

#data = response.read()
#i = data.find("device_id=")
#if(i != -1):
	# Device id and other default configurations are copied to conf.py, for use by other programs
device_id = 1;#data[10:];
fd = open("./conf.py", "w");
with open("./defaults.py", "r") as df:
	for line in df:
		fd.write(line);
fd.write("device_id = \""+str(device_id)+"\"\n");
fd.close();
#else:
#	print "Could not get device id." # save it to logs

# Create Shared Memory segments using the keys
try:
	tone_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_tone	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	tone_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_tone);
try:
	offhook_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_offhook	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	offhook_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_offhook);
try:
	endip_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_endip	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	endip_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);
try:
	convo_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_convo	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	convo_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
try:
	dtmf_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_dtmf	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	dtmf_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_dtmf);
try:
	inccall_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_inccall	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	inccall_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_inccall);
try:
	calls_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_calls	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	calls_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_calls);
try:
	ringphone_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_ringphone	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	ringphone_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_ringphone);
try:
	phone_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_phone	, sysv_ipc.IPC_CREX);
except sysv_ipc.ExistentialError:
	phone_shm	 = sysv_ipc.SharedMemory(sharedmem_utils.key_phone);

# Initialize the Shared Memory to specific values
sharedmem_utils.write_to_memory(tone_shm, 'stop');
sharedmem_utils.write_to_memory(offhook_shm, 'onhook');
sharedmem_utils.write_to_memory(endip_shm, '');
sharedmem_utils.write_to_memory(convo_shm, 'stop');
sharedmem_utils.write_to_memory(dtmf_shm, 'stop');
sharedmem_utils.write_to_memory(inccall_shm, 'start');
sharedmem_utils.write_to_memory(calls_shm, 'nocalls');
sharedmem_utils.write_to_memory(ringphone_shm, 'stop');
sharedmem_utils.write_to_memory(phone_shm, 'onhook');

# Start the Off Hook detection program, and the Incoming Call Handler Program
#os.system(defaults.path_inccall);
