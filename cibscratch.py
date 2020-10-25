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

cib=xml2dict.parse("cibadmin.xml")

print(cib)