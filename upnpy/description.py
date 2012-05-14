'''
Created on 14-05-2012

@author: morti
'''

import upnpy, re

from lxml import etree
from xmlutil import genRootDesc
from util import localInterface

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

class DescriptionServerPage(Resource):
    PATTERN_SERVICE_PATH = re.compile('/(?P<type>[^/]+)/(?P<uuid>[^/.]+)(/(?P<serviceId>[^./]+))?')
    PATTERN_DEVICE_PATH = re.compile('/(?P<type>[^/]+)/(?P<uuid>[^.]+).xml')
    
    isLeaf = True
    def __init__(self):
        self.ssdp = upnpy.discovery
        self.localDevices = upnpy.localDeviceManager
        
    def render_GET(self, request):
        #print 'Desc server got request:', request.path
        
        match = self.PATTERN_SERVICE_PATH.search(request.path)
        
        if not match:
            return "ERROR"
        
        resType = match.group('type')
        uuid = match.group('uuid')
        serviceId = match.group('serviceId')        
        
        #print 'UUID:', uuid
        #print 'ServiceID:', serviceId
        
        if resType == 'device':
            return self.renderDeviceXML(request, uuid)
        
        if resType == 'service':
            return self.renderServiceXML(request, uuid, serviceId)
                    
        return "NUTHING"

    def renderDeviceXML(self, request, uuid):
        request.responseHeaders.setRawHeaders('content-type', ['text/xml'])
        device = self.localDevices.getDevice(uuid)        
        return etree.tostring(genRootDesc(device))
    
    def renderServiceXML(self, request, uuid, serviceId):
        request.responseHeaders.setRawHeaders('content-type', ['text/xml'])
        device = self.localDevices.getDevice(uuid)        
        service = device.services[serviceId]
        return etree.tostring(service.genSCPD())
    
    def render_POST(self, request):
        print 'POST:', request
        print dir(request)
    
class DescriptionServer(object):
    def __init__(self):
        self.addr = None
    
    def listen(self):
        self.addr = reactor.listenTCP(0, Site(DescriptionServerPage()), interface=localInterface()) #@UndefinedVariable
        #print "Desc server listening on", self.addr.getHost()
    
    def getHost(self):
        return (self.addr.getHost().host, self.addr.getHost().port)

    def getBaseURL(self):
        return "http://%s:%s" % self.getHost()
    
    def getSCPDURL(self, service):
        if service.device:
            return  "/service/%s/%s.xml" % ( service.device.UDN, service.serviceId )
        else:
            return None
    
    def getControlURL(self, service):
        if service.device:
            return "/control/%s/%s" % ( service.device.UDN, service.serviceId )
        else:
            return None
    
    def getEventSubURL(self, service):
        if service.device:
            return "/event/%s/%s" % ( service.device.UDN, service.serviceId )
        else:
            return None 