# import xml.sax

# from xml.dom import minidom
#
# cibadmin_query_output=minidom.parse('cibadmin.xml')
# cib=cibadmin_query_output.documentElement
# cib_config_sections=cib.getElementsByTagName('configuration')
# cib_status_sections=cib.getElementsByTagName('status')
#
# print(cib_config_sections[0])

#for section in cib_config_sections:

# import xml.etree.ElementTree as ET
# tree = ET.parse('cibadmin.xml')
# cib= tree.getroot()
#
#
#
# print(cib.tag)
#
# for child in cib.iter():
#     cluster_name=cib.find('cluster-name')
#     print(cluster_name)

import xml2dict
import xmltodict


with open('cibadmin.xml','r') as file:
    cib_file = file.read()
#print(cib_file)

cib= xmltodict.parse(cib_file)
print(cib)

# cib=xml2dict.parse(cib_file,schema)
#
# #print(cib)
#
# for k,v in cib.items():
#     cib=k
#     xml_cib_sections=v
#     cib_last_written=xml_cib_sections['@cib-last-written']
#     for k,v in xml_cib_sections.items():
#         if (k=="configuration"):
#             configuration=k
#             xml_configuration_sections=v
#             for k,v in xml_configuration_sections.items():
#  #               print (k,v)
#                 if (k=="crm_config"):
#                     crm_config=k
#                     xml_cluster_property_set=v
#                     for k,v in xml_cluster_property_set.items():
#                         nvpair=k
#                         xml_config_item=v
#                         print (v)
#
# #                    print (xml_cluster_property_set)
# #                    cluster_name=xml_cluster_property_set['@name']
#         elif (k=="status"):
#             status=k
# #            print (k,v)
#
# print ("CIB last written: " + cib_last_written)