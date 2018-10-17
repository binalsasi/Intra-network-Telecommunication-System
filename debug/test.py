import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
sock.sendto("hello", ("192.168.50.1", 30021));
