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
sharedmem_utils.write_to_memory(phone_shm, "onhook");
print "phone status is  : ", "onhook";

"""
convo_shm = sysv_ipc.SharedMemory(sharedmem_utils.key_convo);

convostatus = sharedmem_utils.read_from_memory(convo_shm);
print "convostatus ", convostatus
sharedmem_utils.write_to_memory(convo_shm, 'stop');
convostatus = sharedmem_utils.read_from_memory(convo_shm);
print "convostatus ", convostatus
"""
