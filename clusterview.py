import json
import sys
import datetime

configfile="config.json"
logfile="clusterview.log"

def log_output(logstring):
    try:
        f=open(logfile,'a')
        timestamp=str(datetime.datetime.utcnow().isoformat(timespec='seconds', sep=' '))
        f.write(timestamp+' '+logstring+'\n')
        f.close
    except OSError as e:
        print('Can not write to logfile !')
        print(str(e))


try:
    with open(configfile, encoding='utf-8') as config_json:
        cluster_config = json.load(config_obj)
except NameError:
    log_output('Can not parse json in '+configfile)
    sys.exit()
except OSError as e:
    log_output(str(e))
    sys.exit()






print (cluster_config)



