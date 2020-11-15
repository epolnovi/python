from pssh.clients import ParallelSSHClient
from pssh.clients import SSHClient

hosts = ['node1','node2']


client = ParallelSSHClient(hosts,user='root',pkey='privatekey')



output = client.run_command('cat /var/lib/pacemaker/cib/cib.xml', return_list=True)
print (output)

for host_output in output:
    print ('----------------')
    print (host_output.stderr)
    for line in host_output.stdout:
        print(line)

hostsfile = SSHClient('node1',user='root',pkey='privatekey')
hostsfile.copy_remote_file('/etc/hosts', 'node1_etc_hosts')