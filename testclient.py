"""
   client:
"""

import time
import socket

HOST = '127.0.0.1'  # connect to the local host
PORT = 59999        # connect to this port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))         # connect to the server


    data = s.recv(16384)      # recv data

    print('From server: ' + repr(data))
    time.sleep(5)
    ## could continue communication
    ## OR
    ## look for a delimiter