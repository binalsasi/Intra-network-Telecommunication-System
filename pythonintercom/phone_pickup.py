#!/usr/bin/python2

## TODO we can check for offhook status as condition for start and stop, instead of seperate state variables

from time import sleep
import os
import httplib, urllib
import socket

# For shared memory
import sysv_ipc

# Keys and functions for shared memory
import sharedmem_utils

# Device and Server Confs
import conf


phone_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_phone);

phone_status = sharedmem_utils.read_from_memory(phone_shm);
print "phone status was : ", phone_status;
sharedmem_utils.write_to_memory(phone_shm, "offhook");
print "phone status is  : ", "offhook";
