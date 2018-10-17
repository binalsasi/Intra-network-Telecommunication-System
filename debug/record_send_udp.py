#!/usr/bin/python
import sys
import pyaudio
import time;
import socket
from threading import Thread

# For SharedMemory functions
import sysv_ipc
import sharedmem_utils
import conf

log = open("logs/record_send_udp.log", 'w', 0);
log.write("record_send_udp.py started to run\n");

convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
endip_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_endip);

convostatus = sharedmem_utils.read_from_memory(convo_shm);
endip = "192.168.50.1" #sharedmem_utils.read_from_memory(endip_shm);

log.write("shared memory obtained and endip = " + endip + "\n");

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

log.write("PyAudio params : CHUNK " + str(CHUNK) + " FORMAT paInt16 CHANNELS " + str (CHANNELS) + " RATE " + str(RATE));

frames = []

def udpStream():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log.write("Created socket. And started sending data\n");
    count = 1
    # TODO use convo shm as breaker
    while True:
        if len(frames) > 0:
            udp.sendto(frames.pop(0), (endip, conf.commport))
            print "sent frame ", str(count)
            count += 1

    log.write("stopped sending data");
    udp.close()

def record(stream, CHUNK):
    # TODO use convo shm as breaker
    log.write("Started to record audio");
    while True:
        try:
            frames.append(stream.read(CHUNK))
        except IOError:
            print "IOError. Doing nothing"
    log.write("Stopped recording audio");

p = pyaudio.PyAudio()
log.write("started pyAudio");

stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK,
                )

Tr = Thread(target = record, args = (stream, CHUNK,))
Ts = Thread(target = udpStream)
Tr.setDaemon(True)
Ts.setDaemon(True)
Tr.start()
log.write("Started record thread");
Ts.start()
log.write("Started udp thread");
Tr.join()
Ts.join()


"""
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
convostatus = "run";
while convostatus != 'stop':
    data = stream.read(CHUNK)
    i+=1;
    print "added to frames, ", str(i)
    sock.sendto(data, (endip, conf.commport))
    #convostatus = sharedmem_utils.read_from_memory(convo_shm);

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()
"""
