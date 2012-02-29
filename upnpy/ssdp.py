#-*- coding: utf-8 -*-
"""
    This is simple SSDP implementation.
"""

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import threads

from upnpy import USER_AGENT
from upnpy.xmlutil import DeviceDescriptionParser
from threading import Lock
import os, re
import uuid
import socket

#from device import parseRootDeviceDesc

class SSDPUnicast(DatagramProtocol):
    packetHandler = None
    
    def __init__(self, ssdpPacketHandler):
        self.packetHandler = ssdpPacketHandler
    
    def datagramReceived(self, datagram, addr):
        #print "Unicast data!"
        self.packetHandler.datagramReceived(datagram, addr)

class SSDPMulticast(DatagramProtocol):
    packetHandler = None
    
    def __init__(self, ssdpPacketHandler):
        self.packetHandler = ssdpPacketHandler
    
    def datagramReceived(self, datagram, addr):
        #print "Multicast data!", datagram
        self.packetHandler.datagramReceived(datagram, addr)

        
class SSDP(object):
    
    SSDP_PORT = 1900
    SSDP_ADDR = "239.255.255.250"
    INADDR_ANY = "0.0.0.0"
    
    TYPE_OK = 0
    TYPE_NOTIFY = 1
    TYPE_SEARCH = 2
    
    SEARCH_TPL = 'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: %s\r\nST: %s\r\n\r\n'
    
    NOTIFY_TPL = 'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nCACHE-CONTROL: max-age = %s\r\nLOCATION: %s\r\n'
    NOTIFY_TPL+= 'NT: %s\r\nNTS: ssdp:alive\r\nSERVER: %s\r\nUSN: %s\r\n'
    #NOTIFY_TPL+= 'BOOTID.UPNP.ORG: %s\r\nCONFIGID.UPNP.ORG: %s\r\nSEARCHPORT: %s\r\n'
    NOTIFY_TPL+= '\r\n'
    
    def __init__(self):
        self._cache = {}
        self._localDevices = {}
        self.deviceFoundHandlers = []
        self.descriptionParser = DeviceDescriptionParser()
        
        
    def listen(self):
        self.unicast = reactor.listenUDP(0, SSDPUnicast(self)) #@UndefinedVariable
        self.multicast = reactor.listenMulticast(self.SSDP_PORT, SSDPMulticast(self), #@UndefinedVariable
                                                 listenMultiple = True)
        self.multicast.setTTL(5)
        self.multicast.joinGroup(self.SSDP_ADDR)

            
        self.descServer = reactor.listenTCP(12345, Site(DescriptionServerPage(self))) #@UndefinedVariable
        #print 'Started description server on %s:%s' % (self.descServer.getHost().host, self.descServer.getHost().port)
        
    def startProtocol(self):
        pass    
        
    
    def datagramReceived(self, datagram, addr):
        lines = datagram.strip().split('\r\n')
        #print "Server received: ", repr(addr), lines
        print "Server received: ", lines
        

        try:        
            data = {}
            data['type'] = None        
            
            if '200 OK' in lines[0].upper():
                data['type'] = SSDP.TYPE_OK
            elif 'NOTIFY' in lines[0].upper():
                data['type'] = SSDP.TYPE_NOTIFY
            elif 'M-SEARCH' in lines[0].upper():
                data['type'] = SSDP.TYPE_SEARCH
            else:
                print 'Unknown packet type:', lines[0]
                
            del lines[0]
    
            for field in lines:
                if ':' in field:
                    name, value = field.split(':', 1)
                    name, value = [name.strip().upper(), value.strip()]
                    data[name] = value
            
            # Check if we've found the device
            if 'LOCATION' in data.keys():
#                if 'USN' in data.keys():                    
#                    match = re.search('(uuid:[^:]*)', data['USN'])
#                    print 'MATCH:', match.group(1)
#                    if match != None and match.group(1) in self._localDevices.keys():
#                        return # Its our local device so don't bother
                    
                #print addr, data
                def inner_parseDeviceInfo():
                    location = data['LOCATION']                    
                    try: # Try to parse the device XML           
                        device = self.descriptionParser.parse(location)
                        return device
                    except:
                        pass
                        import traceback
                        import sys
                        traceback.print_exc(file=sys.stderr)
                    return None
                    

                def inner_resultCallBack(device):
                    if device != None and device.UDN not in self._cache.keys():
                        self._cache[device.UDN] = device
                        print self._cache
                        for handler in self.deviceFoundHandlers:
                            handler(data, device)
                
                
                UDN = None
                if 'USN' in data.keys():                    
                    match = re.search('(uuid:[^:]*)', data['USN'])
                    UDN = match.group(1)
                print 'LOCATION:', data['LOCATION']
#                if data['LOCATION'] not in self._cache.keys():
                if UDN not in self._cache.keys():
                    print UDN
                    print self._cache.keys()
                    threads.deferToThread(inner_parseDeviceInfo).addCallback(inner_resultCallBack)
                                
        except Exception as e:
            print repr(e)
            
        
    def search(self, target='ssdp:all', mx=3, addr=None):
        #msg = 'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: %s\r\nST: %s\r\n\r\n' % (mx, target)
        msg = self.SEARCH_TPL % (mx, target)
        
        if not addr:
            self.unicast.write(msg, (self.SSDP_ADDR, self.SSDP_PORT))
        else:
            self.unicast.write(msg, addr)
        
        #msg = 'M-SEARCH * HTTP/1.1\r\nHOST: 192.168.0.114:1900\r\nMAN: "ssdp:discover"\r\nMX: %s\r\nST: %s\r\n\r\n' % (mx, target)
        #self.transport.write(msg, ('192.168.0.114', self.SSDP_PORT))
        #self.transport.write(msg, ('127.0.0.1', self.SSDP_PORT))
    
    def alive(self, device, maxAge=1800, spreadInTime=True, spreadSpan=30):
        
        # TODO: poprawic aby uruchamial sie watek i rozkladal 
        # komunikaty rownomiernie w czasie
        print self.descServer.getHost().host
        path = '/device/%s.xml' % device.UDN
        baseURL = "http://%s:%s" % ('localhost', self.descServer.getHost().port)
        rootDescURL = "%s%s" % (baseURL, path)        
        device.rootDescURL = rootDescURL
        device.baseURL = baseURL
        
        self._localDevices[device.UDN] = device
        
        TPL = self.NOTIFY_TPL % (maxAge, rootDescURL, "%s", USER_AGENT, "%s")
        addr = (self.SSDP_ADDR, self.SSDP_PORT)
        self.unicast.write(TPL % ("upnp:rootdevice", device.UDN+"::"+device.deviceType), addr)
        self.unicast.write(TPL % (device.deviceType, device.UDN+"::"+device.deviceType), addr)
        self.unicast.write(TPL % (device.UDN, device.UDN+"::"+device.deviceType), addr)
        
        # TODO: notify about subdevices
        #for device in device.devices.values():
        #    self.unicast.write(TPL % (service.serviceType, device.UDN+"::"+service.serviceType), addr)
            
        for service in device.services.values():
            service.SCPDURL = '/service/%s.xml' % (service.serviceId)
            self.unicast.write(TPL % (service.serviceType, device.UDN+"::"+service.serviceType), addr)
        
        #data = self.NOTIFY_TPL % (maxAge, rootDescURL, device.deviceType, USER_AGENT, 
#                                 device.UDN+"::"+device.deviceType)
#        self.unicast.write(data, (self.SSDP_ADDR, self.SSDP_PORT))
        
#        data = self.NOTIFY_TPL % (maxAge, rootDescURL, "upnp:rootdevice", USER_AGENT, 
#                                 device.UDN+"::"+device.deviceType)
#        self.unicast.write(data, (self.SSDP_ADDR, self.SSDP_PORT))
    
    def addHandler(self, handler):
        self.deviceFoundHandlers.append(handler)
            
    def removeHandler(self, handler):
        try: self.deviceFoundHandlers.remove(handler)
        except: pass
        
    def _removeOldDevices(self):
        # TODO: remove old devices
        
        # Call this again in 10.5 seconds
        reactor.callLater(10.5, self._removeOldDevices) #@UndefinedVariable
        
    def _genUUID(self, name):
        return uuid.uuid5(uuid.NAMESPACE_URL, name)
    
    
    @property
    def devices(self):
        return self._cache.values()
    
    @property
    def localDevices(self):
        return self._localDevices.values()
        
        
#class DescriptionServer(Protocol):
#    def __init__(self, ssdp):
#        self.ssdp = ssdp
#        
#    def connectionMade(self):
#        print 'Connection made'
#    
#    def dataReceived(self, data):
#        print 'Description server received:', data
#        self.transport.write('Hello')        

from upnpy.xmlutil import genRootDesc
from lxml import etree

class DescriptionServerPage(Resource):
    isLeaf = True
    def __init__(self, ssdp):
        self.ssdp = ssdp
        
    def render_GET(self, request):
        print 'Desc server got request:', request.path
        
        match = re.search('/([^/]+)/([^.]+).xml', request.path)
        if match == None:
            return "ERROR"
        
        resType = match.group(1)
        resId = match.group(2)
                
        
        if resType == 'device':
            request.responseHeaders.setRawHeaders('content-type', ['text/xml'])            

            device = self.ssdp._localDevices[resId]
            return etree.tostring(genRootDesc(device))
    
        if resType == 'service':
            request.responseHeaders.setRawHeaders('content-type', ['text/xml'])
            
            for device in self.ssdp._localDevices.values():
                if resId in device.services.keys():
                    service = device.services[resId]
                    return etree.tostring(service.genSCPD())
                    
        return "NUTHING"
