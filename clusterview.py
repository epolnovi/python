
import argparse
import datetime

import pickle
import sys

from cluster import PacemakerCluster
from resource import Resource
from cluster_logging import Logging
from threading import Thread
from tabulate import tabulate

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

    with open('sites.p','rb') as pickle_file:
        data=pickle.load(pickle_file)

    pickle_data=pickle.dumps(data)
    full_message=bytes(f"{len(pickle_data):<{HEADERSIZE}}", 'utf-8')+pickle_data # construct message header
    conn.send(full_message)
    print (len(pickle_data))
    print (len(full_message))
    conn.close

def clusterview_update_data(configfile):
    while True:
        sitelist=PacemakerCluster.load_config(configfile)
        with open("sites.p", "wb") as f:
            pickle.dump(sitelist, f)

def start_clusterview_server():
    s = socket.socket()  # open a socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevent script from blocking tcp port
    s.bind((foreign_address, tcp_port))  # bind to a host and port
    s.listen(5)  # start listening

    while True:  # loop for connections ( each in a parallel thread )
        conn, addr = s.accept()  # block and wait for incoming connections
        Logging.log_output("Connection from " + str(addr))
        server_thread = Thread(target=clusterview_server, args=(conn,))  # create a new thread
        server_thread.start()  # start it

    s.close() # This will never be reached...

def receive_data(serverhost):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverhost, tcp_port))

    full_msg = b''
    new_msg = True
    message_header = int(s.recv(HEADERSIZE))

    remaining_bytes = message_header
    read_buffer_size = 0
    while remaining_bytes > 0:
        if remaining_bytes <BUFFERSIZE:
            read_buffer_size = remaining_bytes
        else:
            read_buffer_size = BUFFERSIZE
        full_msg=full_msg + s.recv(read_buffer_size)
        remaining_bytes = remaining_bytes - read_buffer_size

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

    sitelist=pickle.loads(receive_data(args.client[0]))

    sitename=''
    cluster_name=''
    node_name=''
    node_resources=''

    output_table=[]
    print_header=['Sitename','Cluster','Resourcename','Resourcegroup','Class','Type']

    for site in sitelist:
        sitename=site.sitename

        output_table.append([sitename,"","","","",""])

        for cluster in site.clusters:
            cluster_name=cluster.cluster_name

            output_table.append(["",cluster_name,"",])

            for resource in cluster.cluster_resources:
                node_resources=resource.resource_name
                node_group=resource.resource_group
                node_class=resource.resource_class
                node_type=resource.resource_type

                output_table.append(["","",node_resources,node_group,node_class,node_type])

    print (output_table)
    print (tabulate(output_table,headers=print_header,tablefmt='simple'))

    pass
    #




