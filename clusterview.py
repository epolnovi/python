import datetime
import json
import sys
import pssh
import random
from pssh.clients import SSHClient

# json made with https://jsoneditoronline.org/

configfile="config.json"
logfile="clusterview.log"

class Site:

    def __init__(self,sitename,clusters):
        self.sitename=sitename
        self.clusters=clusters

class Cluster:

    def __init__(self,
                 cluster_name,
                 administrator,
                 designated_coordinator="unknown",
                 ssh_keyfile,
                 ssh_user,
                 ssh_passwdfile,
                 ssh_port,
                 nodes="",
                 cib=""):
        self.cluster_name=cluster_name
        self.administrator=administrator
        self.designated_coordinator=designated_coordinator
        self.ssh_keyfile=ssh_keyfile
        self.ssh_user=ssh_user
        self.ssh_passwdfile=ssh_passwdfile
        self.ssh_port=ssh_port
        self.nodes=nodes
        self.cib=cib

        @property
        def cib(self):
            return self.__cib

        @cib.setter
        def cib (self, cib_value):
            self.cib=cib_value

        @property
        def ssh_keyfile(self):
            return self.__ssh_keyfile

        @ssh_keyfile.setter
        def ssh_keyfile (self, ssh_keyfile_value):
            self.ssh_keyfile=ssh_keyfile_value

        @property
        def ssh_user(self):
            return self.__ssh_user

        @ssh_user.setter
        def ssh_user (self, ssh_user_value):
            self.ssh_user=ssh_user_value

        @property
        def ssh_passwdfile(self):
            return self.__ssh_passwdfile

        @ssh_passwdfile.setter
        def ssh_passwdfile (self, ssh_passwdfile_value):
            self.ssh_passwdfile=ssh_passwdfile_value

        @property
        def ssh_port(self):
            return self.__ssh_port

        @ssh_port.setter
        def ssh_port(self, ssh_port_value):
            self.ssh_port=self.sshport_value


        # update cluster cib. If DC is unknown, make a random host DC as bootstrap until crm_mon output catches up

    def update_cib(self):

        if (self.designated_coordinator=="unknown"):
            dc_node_list =[]
            for dc_ip in self.nodes:
                dc_node_list.append(dc_ip.node_ipaddress)
                self.designated_coordinator=random.choice(dc_node_list)

        cluster_cib=SSHClient(self.designated_coordinator,s)



        pass




class Node:

    def __init__(self,
                 node_name,
                 node_ipaddress,
                 node_fqdn,
                 node_status="unknown"):
        self.node_name=node_name
        self.node_ipaddress=node_ipaddress
        self.node_fqdn=node_fqdn
        self.node_status=node_status

        @property
        def node_name(self):
            return self.__node_name

        @node_name.setter
        def node_name (self, node_name_value):
            self.node_name=node_name_value

        @property
        def node_ipaddress(self):
            return self.__node_ipaddress

        @node_ipaddress.setter
        def node_ipaddress (self, node_ipaddress_value):
            self.node_name=node_ipaddress_value

        @property
        def node_fqdn(self):
            return self.__node_fqdn

        @node_fqdn.setter
        def node_fqdn (self, node_fqdn_value):
            self.node_fqdn=node_fqdn_value


        @property
        def node_status(self):
            return self.__node_status

        @node_status.setter
        def node_status(self, ssh_port_value):
            self.node_status=self.node_status
#class Environment:
#    def __init__(self, environment, cluster_name,administrator,vip_address,vip_fqdn,nodes):

# Function to log messages to a logfile

def log_output(logstring):
    try:
        f=open(logfile,'a')
        timestamp=str(datetime.datetime.utcnow().isoformat(timespec='seconds', sep=' '))
        f.write(timestamp+' '+logstring+'\n')
        f.close
    except OSError as e:
        print('Can not write to logfile !')
        print(str(e))

# import settings from config.json

try:
    with open(configfile, encoding='utf-8') as config_json:
        cluster_config = json.load(config_json)
except NameError:
    log_output('Can not parse json in '+configfile)
    sys.exit()
except OSError as e:
    log_output(str(e))
    sys.exit()

configuration=cluster_config['configuration']
privatekey=configuration['global_private_key_file']


sites=cluster_config['sites']

sitelist=[]

for site in cluster_config['sites']:

    clusterlist=[]

    for cluster in site['clusters']:

        nodelist=[]

        for node in cluster['nodes']:
            nodelist.append(Node(
                node_name=node['nodename'],
                node_ipaddress=node['ipaddress'],
                node_fqdn=node['fqdn']
            ))

        clusterlist.append(Cluster(
            cluster_name=cluster['clustername'],
            administrator=cluster['administrator'],
            ssh_keyfile=node['ssh_keyfile'],
            ssh_user=node['ssh_user'],
            ssh_passwdfile=node['ssh_passwdfile'],
            ssh_port=node['ssh_port'],
            nodes=nodelist
        ))

    sitelist.append(Site(
        sitename=site['sitename'],
        clusters=clusterlist
    ))

for site in sitelist:
    for cluster in site.clusters:
        cluster.update_cib()