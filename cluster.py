import random

class PacemakerCluster:

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
        self.cluster_name = cluster_name
        self.administrator = administrator
        self.designated_coordinator = designated_coordinator
        self.ssh_keyfile = ssh_keyfile
        self.ssh_user = ssh_user
        self.ssh_passwdfile = ssh_passwdfile
        self.ssh_port = ssh_port
        self.cluster_resources = cluster_resources
        self.nodes = nodes
        self.cibxml = cibxml
        self.cib = cib
        self.crmxml = crmxml
        self.crm = crm
        self.cluster_status = cluster_status

        @property
        def cluster_name(self):
            return self.__cluster_name

        @property
        def designated_coordinator(self):
            return self.__designated_coordinator

        @designated_coordinator.setter
        def designated_coordinator(self, designated_coordinator_value):
            log_output("Setting designated coordinator of cluster {} to {}".format(self.cluster_name,
                                                                                   designated_coordinator_value))
            self.designated_coordinator = designated_coordinator_value

        @property
        def cibxml(self):
            return self.__cibxml

        @cibxml.setter
        def cibxml(self, cibxml_value):
            self.cibxml = cibxml_value

        @property
        def cib(self):
            return self.__cib

        @cib.setter
        def cib(self, cib_value):
            self.cib = cib_value

        @property
        def ssh_keyfile(self):
            return self.__ssh_keyfile

        @ssh_keyfile.setter
        def ssh_keyfile(self, ssh_keyfile_value):
            self.ssh_keyfile = ssh_keyfile_value

        @property
        def ssh_user(self):
            return self.__ssh_user

        @ssh_user.setter
        def ssh_user(self, ssh_user_value):
            self.ssh_user = ssh_user_value

        @property
        def ssh_passwdfile(self):
            return self.__ssh_passwdfile

        @ssh_passwdfile.setter
        def ssh_passwdfile(self, ssh_passwdfile_value):
            self.ssh_passwdfile = ssh_passwdfile_value

        @property
        def ssh_port(self):
            return self.__ssh_port

        @ssh_port.setter
        def ssh_port(self, ssh_port_value):
            self.ssh_port = self.sshport_value

    # update cluster cib. If DC is unknown, make a random host DC as bootstrap until crm_mon output catches up
    def update_cib(self):

        if (self.designated_coordinator == "unknown"):
            dc_node_list = []
            for dc_ip in self.nodes:
                dc_node_list.append(dc_ip.node_ipaddress)
            self.designated_coordinator = random.choice(dc_node_list)
        try:
            log_output("Downloading CIB from {}".format(self.designated_coordinator))
            ssh_client = SSHClient(self.designated_coordinator,
                                   user=self.ssh_user,
                                   pkey=self.ssh_keyfile,
                                   timeout=1,
                                   num_retries=1)
            node_ssh_output = ssh_client.run_command('cat /var/lib/pacemaker/cib/cib.xml')
            for line in node_ssh_output.stdout:
                self.cibxml = self.cibxml + line + '\n'
            self.cluster_status = "Reachable"
            self.cib = xmltodict.parse(self.cibxml)
        except:
            log_output("Can not download CIB.xml from " + self.designated_coordinator)
            self.designated_coordinator = "unknown"  # if it fails, set it to ynknown, hopefully next random pick will be more succesful
            self.cluster_status = "Unreachable"  # Consider whole cluster offline until the next random host answers.
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

    def update_nodes(self, node_name, node_online_status, node_resources, node_id):
        for node in self.nodes:
            if (node.nodename == self.node_name):
                node.node_online_status = node_online_status
                node.node_resources = node_resources
                node.node_id = node_id

