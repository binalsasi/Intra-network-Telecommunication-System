#!/usr/bin/python2
import pyaudio
import socket
from threading import Thread
import sysv_ipc
import sharedmem_utils
import conf
import time
import wave

# SharedMemory segments to control the activity of the program. Stop when needed.
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
convostatus = sharedmem_utils.read_from_memory(convo_shm);

frames = []

log = open("logs/serversave2.log", "w", 0);
log.write("serversave is started " + str(time.time()) + "\n");

# Receive UDP data and add them to frames
# If compression was used, decrypt it here before adding to frames
def udpStream(CHUNK):
	global log;
	global convostatus;
	global convo_shm;
	global frames;

	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.bind((conf.localhost, conf.commport))
	udp.setblocking(0);

	num = 0

	while convostatus != 'stop':
		try:
			soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
			print "received size ", str(len(soundData)), " num ", str(num);
			num += 1;
			frames.append(soundData)
		except socket.error:
			"Do Nothing";
		convostatus = sharedmem_utils.read_from_memory(convo_shm);

	udp.close()

	log.write("closed. sizeof audio : " + str(len(frames)) + " " + str(time.time()) + "\n");

	wf = wave.open("inc1.wav", 'wb')
	wf.setnchannels(1)
	wf.setsampwidth(2)
	wf.setframerate(44100)
	wf.writeframes(b''.join(frames))
	wf.close()


# Play data in the frames, to the current audio out
def play(stream, CHUNK):
	BUFFER = 10
	while convostatus != 'stop':
		if len(frames) == BUFFER:
			while convostatus != 'stop':
				if(len(frames) != 0):
					stream.write(frames.pop(0), CHUNK)
				convostatus = sharedmem_utils.read_from_memory(convo_shm);
		convostatus = sharedmem_utils.read_from_memory(convo_shm);

# The two functions, udpStream and play are run in different threads
if __name__ == "__main__":
    FORMAT = pyaudio.paInt16
    CHUNK = 8192
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    output = True,
                    frames_per_buffer = CHUNK,
                    )

    Ts = Thread(target = udpStream, args=(CHUNK,))
    Ts.setDaemon(True)
    Ts.start()
    Ts.join()
