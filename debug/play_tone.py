#!/usr/bin/python
import pyaudio
import wave
import sys

# For SharedMemory functions
import sysv_ipc
import sharedmem_utils

# Path to various tones and audios
dialtone="./sounds/dialtone7s.wav";
ringingtone="./sounds/ringingtone8.wav";
timeouttone="./sounds/timeout.wav";
busytone="./sounds/busy.wav";
offline="./sounds/offline.wav";
invalidnumber="./sounds/invalidnumber.wav";
nonexistant = "./sounds/nonexistantnumber.wav";

log = open("logs/playtune.log", 'a', 0);

if(len(sys.argv) < 2):
	print "Usage play_tone.py dial|ringing|timeout|busy|offline|invalid|nonexistant"
        log.write("erroneous call\n");
else:
	option = sys.argv[1];
	if option == "dial":
		filename = dialtone;
	elif option == "ringing":
		filename = ringingtone;
	elif option == "timeout":
		filename = timeouttone;
	elif option == "busy":
		filename = busytone;
	elif option == "offline":
		filename = offline;
	elif option == "invalid":
		filename = invalidnumber;
	elif option == "nonexistant":
		filename = nonexistant;
	else:
		filename = "none";
		print "Usage play_tone.py dial|ringing|timeout|busy|offline|invalid"
        log.write("option = " + option);

	if(filename != "none"):
		tone_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_tone);

		CHUNK = 8192
		RATE = 44100
		
		wf = wave.open(filename, 'rb')

		# Create audio object and start streaming
		p = pyaudio.PyAudio()
		stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
		                channels=wf.getnchannels(),
        		        rate=RATE,
        		        output=True,
                                frames_per_buffer=CHUNK)

		# Read CHUNK sized frames from the wave file
		data = wf.readframes(CHUNK)

                log.write("starting to play\n");
                
		# Play the tone until it is stopped explicitly
		playstatus = sharedmem_utils.read_from_memory(tone_shm);
		while data != '' and playstatus != 'stop':
		    stream.write(data)
		    data = wf.readframes(CHUNK)
		    playstatus = sharedmem_utils.read_from_memory(tone_shm);


                log.write("stopped playing. hook status : " + playstatus);
		stream.stop_stream()
		stream.close()
		p.terminate()
sys.exit();
