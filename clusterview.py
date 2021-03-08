import argparse
import datetime
import json
import pickle
import sys


from cluster import PacemakerCluster
from resource import Resource


# json made with https://jsoneditoronline.org/


class Primitive:
    pass





# class Resourcegroup:
#     def __init__(self,resource_group_name,resource_group_resources=""):
#         self.resource_group_name=resource_group_name
#         self.resource_group_name=resource_group_resources

class Site:

    def __init__(self, sitename, clusters):
        self.sitename = sitename
        self.clusters = clusters

    def __str__(self):
        return self.sitename

        @property
        def clusters(self):
            return self.__clusters

        @clusters.setter
        def clusters(self, clusters_value):
            self.clusters = clusters_value

# Cluster Information Base

class Node:
    def __init__(self,
                 node_name,
                 node_ipaddress,
                 node_fqdn,
                 node_online_status="unknown",
                 node_resources="",
                 node_id=""):
        self.node_name = node_name
        self.node_ipaddress = node_ipaddress
        self.node_fqdn = node_fqdn
        self.node_online_status = node_online_status
        self.node_resources = node_resources

        @property
        def node_name(self):
            return self.__node_name

        @node_name.setter
        def node_name(self, node_name_value):
            self.node_name = node_name_value

        @property
        def node_ipaddress(self):
            return self.__node_ipaddress

        @node_ipaddress.setter
        def node_ipaddress(self, node_ipaddress_value):
            self.node_name = node_ipaddress_value

        @property
        def node_fqdn(self):
            return self.__node_fqdn

        @node_fqdn.setter
        def node_fqdn(self, node_fqdn_value):
            self.node_fqdn = node_fqdn_value

        @property
        def node_status(self):
            return self.__node_status

        @node_status.setter
        def node_status(self, ssh_port_value):
            self.node_status = self.node_status


# Function to log messages to a logfile

def log_output(logstring):
    try:
        f = open(logfile, 'a')
        timestamp = str(datetime.datetime.utcnow().isoformat(timespec='seconds', sep=' '))
        f.write(timestamp + ' ' + logstring + '\n')
        f.close
    except OSError as e:
        print('Can not write to logfile !')
        print(str(e))


# get settings from config.json

def load_config(configfile):
    try:
        with open(configfile, encoding='utf-8') as config_json:
            cluster_config = json.load(config_json)
    except NameError:
        log_output('Can not parse json in ' + configfile)
        sys.exit()
    except OSError as e:
        log_output(str(e))
        sys.exit()

    configuration = cluster_config['configuration']
    privatekey = configuration['global_private_key_file']
    ssh_host_timeout = configuration['ssh_host_timeout']
    ssh_host_retries = configuration['ssh_host_retries']
    global_interval_timer = configuration['global_interval_timer']

    sites = cluster_config['sites']

    sitelist = []

    for site in cluster_config['sites']:

        clusterlist = []

        for cluster in site['clusters']:

            nodelist = []

            for node in cluster['nodes']:
                nodelist.append(Node(
                    node_name=node['nodename'],
                    node_ipaddress=node['ipaddress'],
                    node_fqdn=node['fqdn']
                ))

            clusterlist.append(PacemakerCluster(
                cluster_name=cluster['clustername'],
                administrator=cluster['administrator'],
                ssh_keyfile=cluster['ssh_keyfile'],
                ssh_user=cluster['ssh_user'],
                ssh_passwdfile=cluster['ssh_passwdfile'],
                ssh_port=cluster['ssh_port'],
                nodes=nodelist
            ))

        sitelist.append(Site(
            sitename=site['sitename'],
            clusters=clusterlist
        ))

    for site in sitelist:
        for cluster in site.clusters:

            # Update objects with data from CIB first

            cluster.update_cib()
            cluster.update_crm()
            # if the cluster is deemed unreachable, the cib and arm will be empty.
            if cluster.cluster_status != "Unreachable":
                resource_list = []
                # print (cluster.cluster_name)
                for cib_resource_section in (cluster.cib['cib']['configuration']['resources'].items()):

                    # section can be primitive, or be group. Groups consist of primitives. Iterate twice.

                    if cib_resource_section[0] == "primitive":

                        for primitive in cib_resource_section[1]:
                            resource_list.append(Resource( 
                                resource_name=primitive['@id'],
                                resource_class=primitive['@class'],
                                resource_type=primitive['@type']
                            ))


                    elif cib_resource_section[0] == "group":

                        for primitive_group in cib_resource_section[1]:

                            group_name = primitive_group['@id']

                            for primitive in primitive_group['primitive']:
                                resource_list.append(Resource(
                                    resource_name=primitive['@id'],
                                    resource_class=primitive['@class'],
                                    resource_type=primitive['@type'],
                                    resource_group=group_name
                                ))

                for crm_resource_section in (cluster.crm['pacemaker-result']['resources'].items()):
                    # in crm_mon output, primitives are called resources
                    if crm_resource_section[0] == "resource":
                        for primitive in crm_resource_section[1]:
                            resource_name = primitive['@id']
                            resource_agent = primitive['@resource_agent']
                            resource_location = primitive['node']['@name']

                            # iterate through existing resource_list and add the agent and running location if the name matches
                            for resource in resource_list:
                                if resource.resource_name == resource_name:
                                    resource.resource_agent = resource_agent
                                    resource.resource_location = resource_location

                    elif crm_resource_section[0] == "group":
                        group_list = []
                        for primitive_group in crm_resource_section[1]:
                            # in crm_mon output, primitives are called resources
                            for primitive in primitive_group['resource']:
                                resource_name = primitive['@id']
                                resource_agent = primitive['@resource_agent']
                                resource_location = primitive['node']['@name']
                                for resource in resource_list:
                                    if resource.resource_name == resource_name:
                                        resource.resource_agent = resource_agent
                                        resource.resource_location = resource_location

    #        cluster.cluster_resources = resource_list

    #         print ('hello')

    return sitelist


# Main program starts here.
# Parse the commandline


configfile = "config.json"
logfile = "clusterview.log"
privatekey = "id_rsa"  # declare variable now, but will be overwritten from config.json
ssh_host_timeout = 1
ssh_host_retries = 1

parser = argparse.ArgumentParser(description='Clusterview - monitor pacemaker clusters')
group = parser.add_mutually_exclusive_group()
group.add_argument(
    '--server',
    metavar="configfile",
    type=str,
    action="store",
    help='specify the configfile for server mode',
    nargs=1
)

group.add_argument(
    '--client',
    metavar="configfile",
    action="store",
    help='specify the configfile for client mode',
    nargs=1
)

args = parser.parse_args()

if args.server is not None:
    server_config_file = args.server[0]

    sitelist = load_config(server_config_file)
    pickle.dump(sitelist, open("sitelist.p", "wb"))

    print('hello worls')

if args.client is not None:
    print(args.client)
    sitelist = pickle.load(open("sitelist.p", "rb"))

    print("Hello world")

# log_output("Starting clusterview")
# sitelist=load_config(configfile)
#
# pickle.dump( sitelist, open("sitelist.p", "wb"))
