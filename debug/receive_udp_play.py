import pyaudio
import socket
from threading import Thread
import sysv_ipc
import sharedmem_utils
#import conf

localhost = "192.168.50.2"
commport =  30021

# SharedMemory segments to control the activity of the program. Stop when needed.
#convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);
#convostatus = sharedmem_utils.read_from_memory(convo_shm);
 
frames = []

# Receive UDP data and add them to frames
# If compression was used, decrypt it here before adding to frames
def udpStream(CHUNK):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((localhost, commport))
    count = 0
    while True:#convostatus != 'stop':
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(soundData)
	count += 1
	print "received frame ", str(count)
	#convostatus = sharedmem_utils.read_from_memory(convo_shm);

    udp.close()

# Play data in the frames, to the current audio out
def play(stream, CHUNK):
    BUFFER = 10
    while True: #convostatus != 'stop':
            if len(frames) == BUFFER:
                while True: #convostatus != 'stop':
		    if(len(frames) != 0):
	                    stream.write(frames.pop(0), CHUNK)
		    #convostatus = sharedmem_utils.read_from_memory(convo_shm);
	    #convostatus = sharedmem_utils.read_from_memory(convo_shm);

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
    Tp = Thread(target = play, args=(stream, CHUNK,))
    Ts.setDaemon(True)
    Tp.setDaemon(True)
    Ts.start()
    Tp.start()
    Ts.join()
    Tp.join()
