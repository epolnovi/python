import json
import sys
import datetime

configfile="config.json"
logfile="clusterview.log"

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

# build objects from json config

for k,v in cluster_config.items():
    cluster_site=k
    cluster_environment=v
    for k,v in cluster_environment.items():
        cluster=k
        cluster_properties=v
        cluster_name=cluster_properties["name"]
        cluster_administrator=cluster_properties["name"]
        cluster_vipaddress=cluster_properties["vipaddress"]
        cluster_vipfqdn=cluster_properties["vipfqdn"]
        cluster_nodes=cluster_properties["nodes"]
        for k,v in cluster_nodes.items():
            node_name=k
            node_properties=v
            node_ipaddress=node_properties["ipaddress"]
            node_fqdn=node_properties["fqdn"]
            node_sshkey=node_properties["sshkey"]
            node_sshuser=node_properties["sshuser"]
            print (cluster_site, cluster_vipaddress,node_ipaddress,node_fqdn)