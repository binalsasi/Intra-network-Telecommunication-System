"""PyAudio Example: Play a WAVE file."""

import conf
import pyaudio
import wave
import sys
import time;
import socket

# CHUNK was reduced from 8192 to fix the tempo of wavs that were recorded with RATE = 8000
CHUNK = 1024

if len(sys.argv) < 3:
    print("Plays a wave file.\n\nUsage: %s filename.wav endip" % sys.argv[0])
    sys.exit(-1)

log = open("logs/play_saved_wave.log", 'a', 0);
log.write("play tone run. arg : ")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

wf = wave.open(sys.argv[1], 'rb')

endip = sys.argv[2];

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)

while data != '':
    sock.sendto(data, (endip, conf.commport))
    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()

p.terminate()

sock.sendto('hangup', (endip, conf.callport));

