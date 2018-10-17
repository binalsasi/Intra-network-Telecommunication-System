#!/usr/bin/python
import os
import conf

with open("logs/convo.log", 'w') as log:
    log.write("convo.py run");
    
    # This program records from the current audio device and send it to the other device via UDP
    os.system(conf.path_recordsend);
    log.write("called record send");

    # This program receives data sent by the other device and plays it
    os.system(conf.path_receiveplay);
    log.write("called receive play");
