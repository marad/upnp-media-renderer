'''
Created on 13-05-2012

@author: morti
'''

import upnpy
from upnpy.xmlutil import XmlDescriptionBuilder
from upnpy.device import Device
from PyQt4.QtGui import QWidget
from lxml import etree
from upnpy.decorators import MyService

if __name__ == '__main__':
    
    xml = ""
    with open("xml/renderer.xml") as data:
        xmlTpl = data.read()
        xml = xmlTpl % {
            "UUID": upnpy.discovery._genUUID("klopsik"),
            "cmSCPDURL": "",
            "rcSCPDURL": "",
            "eventURL": "",
            "controlURL": "",
            "presentationURL": "http://wp.pl"
            }
    
        
    rootNode = etree.fromstring(xml)
    ns = {
        'dev':'urn:schemas-upnp-org:device-1-0',
        'srv':'urn:schemas-upnp-org:service-1-0'
    }
    devNode = rootNode.xpath("/dev:root/dev:device", namespaces=ns)[0]    
        
    builder = XmlDescriptionBuilder()    
    #dev = builder.buildRootDevice(devNode, { 'LOCATION': 'http://localhost:12345/klops.xml'} )
    dev = Device()
        
    builder.parseNode(devNode, dev, ['deviceList', 'iconList', 'serviceList'])
    
    print dev.friendlyName
    
    window = QWidget()
    window.show()
    
    devs = upnpy.localDeviceManager
    
    print dev
    srv = MyService()
    srv.serviceType = 'SHIT-SERVICE'
    srv.serviceId = 'myservice'
    dev.addService(srv)
    devs.addDevice(dev)
    
    upnpy.run()