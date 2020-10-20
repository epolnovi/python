from __future__ import print_function
import json
import dns.resolver



class Server:

    def __init__(self, name, ipaddresses_strings,hostname,service):
        self._name = name
        self._ipaddresses = list()
        for ipaddress_entry in ipaddresses_strings:
            self._ipaddresses.append(Ipaddress(ipaddress_entry))
        self._hostname = hostname
        self._service = service

    def get_ip(self):
        return (self._ipaddress)

    def get_status(self):
        response=dict()
        for ipaddress in self._ipaddresses:
            response.update({ipaddress:ipaddress.get_status()})
        return response

class Customer:

    def __init__(self, name, servers):
        self._name = name
        self._servers = servers

    def get_server_status(self):
        response=dict()
        for server in self._servers:
            response.update({server._name:server.get_status()})

        return response

class Ipaddress:
    def __init__(self, ipaddress):
        self._ipaddress = ipaddress

    def __repr__(self):
        return (self._ipaddress)

    def get_status(self):
        return ("online")

class Service:
    def __init__(self,service):
        self._service=service

data = {
    "google":{
        "dns server":{
            "application":"google dns server",
            "hostname":"dns.google.com",
            "service":"icmp"
             },

        },
    "microsoft": {
        "hotmail server": {
            "application": "hotmail server",
            "hostname": "www.hotmail.com",
            "service": "http"
            },
    }
}
customers=list()
for customer_name, servers_data in data.items():

    servers=list()
    for server_name,server_data in servers_data.items():
        answers = dns.resolver.query(server_data["hostname"], 'A')
        server_ipaddresses = list()

        for rdata in answers:
            server_ipaddresses.append(rdata.address)
        servers.append(Server(
            name=server_name,
            ipaddresses_strings=server_ipaddresses,
            hostname=server_data["hostname"],
            service=server_data["service"],))
    customer=Customer(customer_name, servers)
    customers.append(customer)
