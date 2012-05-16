'''
Created on 14-05-2012

@author: morti
'''

import upnpy, re

from lxml import etree
from xmlutil import genRootDesc
from util import localInterface

from soap import SOAPRequestParser, SOAPResponse

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from upnpy import consts
from time import strftime, gmtime

class DescriptionServerPage(Resource):
    PATTERN_SERVICE_PATH = re.compile('/(?P<type>[^/]+)/(?P<uuid>[^/.]+)(/(?P<serviceId>[^./]+))?')
    PATTERN_DEVICE_PATH = re.compile('/(?P<type>[^/]+)/(?P<uuid>[^.]+).xml')
    
    isLeaf = True
    def __init__(self):
        self.ssdp = upnpy.discovery
        self.localDevices = upnpy.localDeviceManager
        self.soapResponse = SOAPResponse()
        self.reqParser = SOAPRequestParser()
        
    def render_GET(self, request):
        #print 'Desc server got request:', request.path
        
        match = self.PATTERN_SERVICE_PATH.search(request.path)
        
        if not match:
            # TODO: return actual SOAP with error
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
        print request
        
        match = self.PATTERN_SERVICE_PATH.search(request.path)
        
        if not match:
            # TODO: return actual SOAP with error
            return "ERROR - Wrong request path"
        
        resType = match.group('type')
        uuid = match.group('uuid')
        serviceId = match.group('serviceId')     
           
        if resType == "control":
            
            headers = request.getAllHeaders()
            soapAction = str(headers['soapaction']).strip('"').strip("'")
            actionName = soapAction.split("#")[1]
            
            print 'Action:', actionName      
        
            device = self.localDevices.getDevice(uuid)
            service = device.services[serviceId]
            
            action = service.actions[actionName]
            
            xml = request.content.getvalue()
            
            args = self.reqParser.parse(action, xml)
            
            try:
                method = getattr(service, actionName)
                outArgs = method(**args)
                resp = self.soapResponse.generate(service, actionName, outArgs)
                
                request.responseHeaders.setRawHeaders('CONTENT-TYPE', ['text/xml'])
                request.responseHeaders.setRawHeaders('SERVER', [consts.USER_AGENT])
                request.responseHeaders.setRawHeaders('DATE', [strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime())])
                return str(resp)
                
            except AttributeError:
                # TODO: send SOAP error message
                return "ERROR - No action"
            
        return "ERROR - Wrong request path"
            
        
    
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