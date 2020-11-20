import datetime
import json
import sys
import random
import xmltodict
from pssh.clients import SSHClient

# json made with https://jsoneditoronline.org/

configfile="config.json"
logfile="clusterview.log"
privatekey="id_rsa"  # declare variable now, but will be overwritten from config.json
ssh_host_timeout=1
ssh_host_retries=1

class Primitive:
  #    def __init__(self, resource_agent):
    pass


class Resource:
    def __init__(self,resource_name, resource_class, resource_type, resource_agent="", resource_group="", resource_status="", resource_location=""):
        self.resource_name=resource_name
        self.resource_class=resource_class
        self.resource_type=resource_type
        self.resource_group=resource_group
        self.resource_agent=resource_agent
        self.resource_status=resource_status
        self.resource_location = resource_location


class Fence_device:
    pass

class Resourcegroup:
    def __init__(self,resource_group_name,resource_group_resources=""):
        self.resource_group_name=resource_group_name
        self.resource_group_name=resource_group_resources

class Site:

    def __init__(self,sitename,clusters):
        self.sitename=sitename
        self.clusters=clusters

    def __str__(self):
        return self.sitename

        @property
        def clusters(self):
            return self.__clusters

        @clusters.setter
        def clusters (self, clusters_value):
            self.clusters=clusters_value

# Cluster Information Base

class Cluster:

    def __init__(self,
                 cluster_name,
                 administrator,
                 ssh_keyfile,
                 ssh_user,
                 ssh_passwdfile,
                 ssh_port,
                 designated_coordinator="unknown",
                 cluster_resources="",
                 nodes="",
                 cibxml="",
                 cib="",
                 crmxml="",
                 crm="",
                 cluster_status=""):
        self.cluster_name=cluster_name
        self.administrator=administrator
        self.designated_coordinator=designated_coordinator
        self.ssh_keyfile=ssh_keyfile
        self.ssh_user=ssh_user
        self.ssh_passwdfile=ssh_passwdfile
        self.ssh_port=ssh_port
        self.cluster_resources=cluster_resources
        self.nodes=nodes
        self.cibxml=cibxml
        self.cib=cib
        self.crmxml=crmxml
        self.crm=crm
        self.cluster_status=cluster_status



        @property
        def cluster_name(self):
            return self.__cluster_name

        @property
        def designated_coordinator(self):
            return self.__designated_coordinator

        @designated_coordinator.setter
        def designated_coordinator(self,designated_coordinator_value):
            log_output("Setting designated coordinator of cluster {} to {}".format(self.cluster_name, designated_coordinator_value))
            self.designated_coordinator=designated_coordinator_value


        @property
        def cibxml(self):
            return self.__cibxml

        @cibxml.setter
        def cibxml (self, cibxml_value):
            self.cibxml=cibxml_value

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
        try:
            log_output("Downloading CIB from {}".format(self.designated_coordinator))
            ssh_client = SSHClient(self.designated_coordinator,
                                   user=self.ssh_user,
                                   pkey=self.ssh_keyfile,
                                   timeout=1,
                                   num_retries=1)
            node_ssh_output=ssh_client.run_command('cat /var/lib/pacemaker/cib/cib.xml')
            for line in node_ssh_output.stdout:
                self.cibxml=self.cibxml+line + '\n'
            self.cluster_status="Reachable"
            self.cib= xmltodict.parse(self.cibxml)
        except:
            log_output("Can not download CIB.xml from "+self.designated_coordinator)
            self.designated_coordinator="unknown"  # if it fails, set it to ynknown, hopefully next random pick will be more succesful
            self.cluster_status="Unreachable" # Consider whole cluster offline until the next random host answers.
            return
        return self.cib
    def update_crm(self):
        try:
            ssh_client = SSHClient(self.designated_coordinator,
                                   user=self.ssh_user,
                                   pkey=self.ssh_keyfile,
                                   timeout=2,
                                   num_retries=2)
            node_ssh_output = ssh_client.run_command('crm_mon --output-as=xml')
            for line in node_ssh_output.stdout:
                self.crmxml = self.crmxml + line + '\n'
            for line in node_ssh_output.stderr:
                log_output(line)
            self.crm = xmltodict.parse(self.crmxml)
        except Exception as e:
            print(e)
            log_output(str(e))
            return e
        return self.crm
    def update_nodes(self, node_name,node_online_status,node_resources,node_id):
        for node in self.nodes:
            if (node.nodename==self.node_name):
                node.node_online_status=node_online_status
                node.node_resources=node_resources
                node.node_id=node_id
class Node:
    def __init__(self,
                 node_name,
                 node_ipaddress,
                 node_fqdn,
                 node_online_status="unknown",
                 node_resources="",
                 node_id=""):
        self.node_name=node_name
        self.node_ipaddress=node_ipaddress
        self.node_fqdn=node_fqdn
        self.node_online_status=node_online_status
        self.node_resources=node_resources

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

# get settings from config.json

def load_config(configfile):

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
    ssh_host_timeout=configuration['ssh_host_timeout']
    ssh_host_retries=configuration['ssh_host_retries']

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

                    if cib_resource_section[0]=="primitive":
                        # print (cib_resource_section[1])

                        for primitive in cib_resource_section[1]:
                            # print (primitive)
                            # print (primitive['@class'])

                            resource_list.append(Resource(
                                resource_name=primitive['@id'],
                                resource_class=primitive['@class'],
                                resource_type=primitive['@type']
                            ))


                    elif cib_resource_section[0]=="group":
                        group_list=[]
                        for primitive_group in cib_resource_section[1]:
                            # print (primitive_group)
                            group_name=primitive_group['@id']

                            for primitive in primitive_group['primitive']:
                                # print (primitive)
                                # print (primitive['@class'])

                                resource_list.append(Resource(
                                    resource_name=primitive['@id'],
                                    resource_class=primitive['@class'],
                                    resource_type=primitive['@type'],
                                    resource_group=group_name
                                ))

                for crm_resource_section in (cluster.crm['pacemaker-result']['resources'].items()):
# in crm_mon output, primitives are called resources
                    if crm_resource_section[0]=="resource":
                        for primitive in crm_resource_section[1]:
                            resource_name=primitive['@id']
                            resource_agent=primitive['@resource_agent']
                            resource_location=primitive['node']['@name']

# iterate through existing resource_list and add the agent and running location if the name matches
                            for resource in resource_list:
                                if resource.resource_name==resource_name:
                                    resource.resource_agent=resource_agent
                                    resource.resource_location=resource_location

                    elif crm_resource_section[0]=="group":
                        group_list=[]
                        for primitive_group in crm_resource_section[1]:
# in crm_mon output, primitives are called resources
                            for primitive in primitive_group['resource']:
                                resource_name = primitive['@id']
                                resource_agent = primitive['@resource_agent']
                                resource_location = primitive['node']['@name']
                                for resource in resource_list:
                                    if resource.resource_name==resource_name:
                                        resource.resource_agent=resource_agent
                                        resource.resource_location=resource_location






            cluster.cluster_resources = resource_list





            print ('hello')





    return sitelist

log_output("Starting clusterview")
sitelist=load_config(configfile)





print ("hello world")