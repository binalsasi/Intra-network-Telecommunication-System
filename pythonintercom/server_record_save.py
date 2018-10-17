#!/usr/bin/python2
import pyaudio
import socket
from threading import Thread
import wave
import sysv_ipc
import sharedmem_utils
import conf
import time;

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

log = open("logs/serversave.log", "w", 0);
log.write("serversave is started " + str(time.time()) + "\n");


# SharedMemory segments to control the activity of the program. Stop when needed.
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
convostatus = sharedmem_utils.read_from_memory(convo_shm);

frames = []

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((conf.localhost, conf.commport))

num=0;

while convostatus != 'stop':
	soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
	frames.append(soundData)
	print "received size ", str(len(soundData)), " num ", str(num);
	num += 1;
	convostatus = sharedmem_utils.read_from_memory(convo_shm);

udp.close()

log.write("closed. sizeof audio : " + str(len(frames)) + " " + str(time.time()) + "\n");

wf = wave.open("outputwav.wav", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(2)
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
