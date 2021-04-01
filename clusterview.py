
import argparse
import datetime

import pickle
import sys

from cluster import PacemakerCluster
from resource import Resource
from cluster_logging import Logging
from threading import Thread

import socket

# json made with https://jsoneditoronline.org/


configfile = "config.json"
logfile = "clusterview.log"
privatekey = "id_rsa"  # declare variable now, but will be overwritten from config.json
ssh_host_timeout = 1
ssh_host_retries = 1
foreign_address=''
tcp_port=59999

HEADERSIZE=10
BUFFERSIZE=1024

Logging.set_logging(logfile,use_logfile=True, verbose_to_terminal=False)

def clusterview_server(conn):
#    while True:  # loop
    with open('sites.p','rb') as pickle_file:
        data=pickle_file.read()

    pickle_data=pickle.dumps(data)
    full_message=bytes(f"{len(pickle_data):<{HEADERSIZE}}", 'utf-8')+pickle_data # construct message header
    conn.send(full_message)
    print (len(pickle_data))
    print (len(full_message))
    conn.close

        # sitelist=pickle.load( open("sites.p", "rb" ))
        # pickle_data=pickle.dumps(sitelist)
        # conn.sendall(pickle_data)  # send data
        # print("Connection closed: " + str(addr))
        # conn.close()  # close connection

def clusterview_update_data(configfile):
    while True:
        sitelist=PacemakerCluster.load_config(configfile)
        with open("sites.p", "wb") as f:
            pickle.dump(sitelist, f)
 #       pickle.dump(sitelist, open("sites.p", "wb"))

def start_clusterview_server():
    server_socket = socket.socket()  # open a socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevent script from blocking tcp port
    server_socket.bind((foreign_address, tcp_port))  # bind to a host and port
    server_socket.listen(5)  # start listening


    while True:  # loop for connections ( each in a parallel thread )
        conn, addr = server_socket.accept()  # block and wait for incoming connections
        print("Connection from " + str(addr))
        server_thread = Thread(target=clusterview_server, args=(conn,))  # create a new thread
        server_thread.start()  # start it

    server_socket.close() # This will never be reached...

def receive_data(serverhost):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverhost, tcp_port))

    full_msg = b''
    new_msg = True
    message_header = int(s.recv(HEADERSIZE))
    # while True:
    #     msg = s.recv(1024)
    #     if new_msg:
    #         print("new msg len:", msg[:HEADERSIZE])
    #         msglen = int(msg[:HEADERSIZE])
    #         print(msglen)
    #         new_msg = False
    #     full_msg += msg
    #
    # print(f"full message length: {msglen}")
    #
    # print(len(full_msg))
    print ("headersize")
    print (message_header)

    remaining_bytes = message_header
    read_buffer_size = 0
    while (remaining_bytes > 0):
        if remaining_bytes <BUFFERSIZE:
            read_buffer_size==remaining_bytes
        else:
            read_buffer_size==BUFFERSIZE
        print (remaining_bytes)
        full_msg=full_msg + s.recv(read_buffer_size)
        remaining_bytes == remaining_bytes - read_buffer_size

    return full_msg


parser = argparse.ArgumentParser(description='Clusterview - monitor pacemaker clusters')
group = parser.add_mutually_exclusive_group()
group.add_argument(
    '--server',
    metavar="configfile",
    type=str,
    action="store",
    help="specify the configfile for server mode",
    nargs=1
)

group.add_argument(
    '--client',
    metavar="server_host",
    action="store",
    help='specify the server to connect to',
    nargs=1
)

parser.add_argument(
    '--port',
    action="store",
    help="specify tcp port number for server or client (default: 59999)."
)


args = parser.parse_args()

# Main server loop

if args.server is not None:
    server_config_file = args.server[0]

    # Start collecting data in a seperate thread

    load_config_thread = Thread(target=clusterview_update_data, args=(server_config_file,), daemon=True)
    load_config_thread.start()
    start_clusterview_server()

if args.client is not None:
    print(args.client)

    server_data=receive_data(args.client[0])
    print ("resultaat:")
    print (server_data)




