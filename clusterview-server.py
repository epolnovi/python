import pickle
from clusterview import log_output,load_config

configfile="config.json"
# logfile="clusterview.log"
# privatekey="id_rsa"  # declare variable now, but will be overwritten from config.json
# ssh_host_timeout=1
# ssh_host_retries=1

log_output("Starting clusterview")



while True:
    sitelist=load_config(configfile)
    with open ('sitelist.p', 'wb') as pickle_file:
        pickle.dump(sitelist,pickle_file)