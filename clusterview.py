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


class Primitive:
    pass

# Function to log messages to a logfile

# def log_output(logstring):
#     try:
#         f = open(logfile, 'a')
#         timestamp = str(datetime.datetime.utcnow().isoformat(timespec='seconds', sep=' '))
#         f.write(timestamp + ' ' + logstring + '\n')
#         f.close
#     except OSError as e:
#         print('Can not write to logfile !')
#         print(str(e))




# Main program starts here.
# Parse the commandline


configfile = "config.json"
logfile = "clusterview.log"
privatekey = "id_rsa"  # declare variable now, but will be overwritten from config.json
ssh_host_timeout = 1
ssh_host_retries = 1
server_host = ''
tcp_port=59999


Logging.set_logging(logfile,use_logfile=True, verbose_to_terminal=False)

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
    metavar="HOST",
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

    sitelist = PacemakerCluster.load_config(server_config_file)
    pickle.dump(sitelist, open("sitelist.p", "wb"))
    data=pickle.dumps(sitelist)


    s = socket.socket()  # open a socket
    s.bind(('', tcp_port))  # bind to a host and port
    s.listen(5)  # start listening


    def handle_connection(conn):
        while True:  # loop to recv data
            conn.sendall(data)  # send data back
        print("Connection closed: " + str(addr))
        conn.close()  # close connection


    while True:  # loop for connections ( each in a parallel thread )
        conn, addr = s.accept()  # block and wait for incoming connections
        print("Connection from " + str(addr))
        t = Thread(target=handle_connection, args=(conn,))  # create a new thread
        t.start()  # start it

    s.close()

    print('hello worls')

if args.client is not None:
    print(args.client)
    sitelist = pickle.load(open("sitelist.p", "rb"))

    print("Hello world")

# log_output("Starting clusterview")
# sitelist=load_config(configfile)
#
# pickle.dump( sitelist, open("sitelist.p", "wb"))
