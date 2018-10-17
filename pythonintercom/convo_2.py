#!/usr/bin/python2
import os
import conf
import time

log = open("logs/convo.log", "w", 0);
log.write("convo is started " + str(time.time()) + "\n");

# This program receives data sent by the other device and saves it
os.system(conf.path_recordsend);
