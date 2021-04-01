"""
   client:
"""

import time
import socket

HOST = '127.0.0.1'  # connect to the local host
PORT = 59999        # connect to this port

import pickle

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    full_msg = b''
    new_msg = True
    while True:
        msg = s.recv(1024)
        if new_msg:
            print("new msg len:",msg[:HEADERSIZE])
            msglen = int(msg[:HEADERSIZE])
            print(msglen)
            new_msg = False

        print(f"full message length: {msglen}")

        full_msg = s.recv(msglen)

        print (len(full_msg))


