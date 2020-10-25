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

for cluster_site, cluster_environment in cluster_config.items():
    cluster=cluster_environment
    for c,d in cluster.items():
        print ("site:"+cluster_site)
        print ('environment:'+str(cluster))
        print ('c'+c)
        print ('d'+ str(d))




