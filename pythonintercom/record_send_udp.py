#!/usr/bin/python2
import sys
import pyaudio
import time;
import socket

# For SharedMemory functions
import sysv_ipc
import sharedmem_utils
import conf

convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
endip_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);

convostatus = sharedmem_utils.read_from_memory(convo_shm);
endip = sharedmem_utils.read_from_memory(endip_shm);

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

# Read audio data from the audio in, and send it to the other device via UDP
frames = []
i=0;
while convostatus != 'stop':
    data = stream.read(CHUNK)
    i+=1;
    print "added to frames, ", str(i)
    sock.sendto(data, (endip, conf.commport))
    convostatus = sharedmem_utils.read_from_memory(convo_shm);

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()
