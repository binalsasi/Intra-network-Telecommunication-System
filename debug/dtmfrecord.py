#!/usr/bin/python
import os
import pyaudio
import time;
import sysv_ipc
import sharedmem_utils
import conf
from sys import exit

log = open("logs/dtmfrecord.log", 'w', 0);
log.write("dtmfrecord was run");

offhook_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_offhook);
offhook_status = sharedmem_utils.read_from_memory(offhook_shm);

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 20

p = pyaudio.PyAudio()

log.write("pyaudio started. params : CHUNK " + str(CHUNK) + " FORMAT paInt16 CHANNELS " + str(CHANNELS) + " RATE " + str(RATE) + " RECORD SECONDS " + str(RECORD_SECONDS));

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")
log.write("recording\n");
frames = []

#offhook_status="offhook";

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    if(offhook_status == "onhook"):
        break;
    offhook_status = sharedmem_utils.read_from_memory(offhook_shm);
    try:
        frames.append(stream.read(CHUNK))
    except IOError:
        print "IOError. Do Nothing";
        
#offhook_status = "offhook";
        
log.write("recording stopped. Offhookstatus : " + offhook_status);
if(offhook_status == "offhook"):
    print("* done recording")
    log.write("recording done\n");


    stream.stop_stream()
    stream.close()
    p.terminate()

    log.write("calling dtmf reader\n");
    os.system(conf.path_dtmf);

    p = pyaudio.PyAudio()
    log.write("pyaudio initialised again with the same params.");

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)
    
    log.write("playing\n");
    while len(frames) > 0:
        if(offhook_status == "onhook"):
            break;
        offhook_status = sharedmem_utils.read_from_memory(offhook_shm);
        try:
            stream.write(frames.pop(0), CHUNK)
        except IOError:
            print "IOError. Do nothing"

    log.write("done playing. offhookstatus : " + offhook_status);

    stream.stop_stream()
    stream.close()

    p.terminate()
else:
    log.write("phone was put on hook");
exit();
