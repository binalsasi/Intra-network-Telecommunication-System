import socket
import sysv_ipc
import sharedmem_utils
import conf


udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.sendto('', (conf.localhost, conf.commport));
udp.close();
