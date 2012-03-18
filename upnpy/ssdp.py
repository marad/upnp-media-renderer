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
from upnpy.xmlutil import XmlDescriptionBuilder
from threading import Lock
from upnpy.device import Device, Service
import os, re
import uuid
import socket
import traceback
import sys

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
        self._lostDevices = {}
        self._lostServices = {}        
        self._localDevices = {}
        self.deviceFoundHandlers = []
        self.serviceFoundHandlers = []
        self.xmlParser = XmlDescriptionBuilder()
        
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
        #print "Server received: ", addr[0], lines
        

        try:        
            data = {}
            data['TYPE'] = None        
            
            if '200 OK' in lines[0].upper():
                data['TYPE'] = SSDP.TYPE_OK
            elif 'NOTIFY' in lines[0].upper():
                data['TYPE'] = SSDP.TYPE_NOTIFY
            elif 'M-SEARCH' in lines[0].upper():
                data['TYPE'] = SSDP.TYPE_SEARCH
            else:
                print 'Unknown packet type:', lines[0]
                
            del lines[0]
    
            for field in lines:
                if ':' in field:
                    name, value = field.split(':', 1)
                    name, value = [name.upper(), value.strip()]
                    data[name] = value
            # Check if we've found the device
            if 'LOCATION' in data.keys():          
                #print addr, data
                #print data['TYPE'], data.keys()
                #if 'USN' in data.keys(): print data['USN']
                def inner_parseDeviceInfo():
                    location = data['LOCATION']                    
                    try: # Try to parse the device XML           
                        #device = self.descriptionParser.parse(location)
                        device = self.xmlParser.build(data)
                        return device
                    except:
                        traceback.print_exc(file=sys.stderr)
                    return None
                                    
                def inner_resultCallBack(entity):
                    if entity != None:
                        if isinstance(entity, Device) and entity.UDN not in self._cache.keys():
                            # save device in cache                            
                            self._cache[entity.UDN] = entity
                            
                            # check if there are some lost embedded devices for this one
                            if entity.UDN in self._lostDevices.keys():
                                for dev in self._lostDevices[entity.UDN]:
                                    entity.addDevice(dev)
                                del self._lostDevices[entity.UDN]
                            
                            # check for lost services
                            if entity.UDN in self._lostServices.keys():
                                for srv in self._lostServices[entity.UDN]:
                                    entity.addService(srv)
                                del self._lostServices[entity.UDN]
                            
                            # add embedded device to it's parent
                            if entity.embedded:            
                                try:                
                                    parentDev = self._cache[entity.parentUDN]
                                    parentDev.addDevice(entity)
                                except KeyError:
                                    # if there's no info about parent device
                                    # we trhow this one into lost devices
                                    #print 'Lost device:', entity.friendlyName
                                    if entity.parentUDN not in self._lostDevices.keys():
                                        self._lostDevices[entity.parentUDN] = []
                                    self._lostDevices[entity.parentUDN].append(entity)
                                
                            # notify clients about new device
                            for handler in self.deviceFoundHandlers:
                                handler(data, entity)
                        elif isinstance(entity, Service):
                            # this entity is service
                            try:
                                # try to add service to its parent device
                                parentDev = self._cache[entity.parentUDN]
                                parentDev.addService(entity)
                            except KeyError:
                                # if error occurs we have no information about parent device
                                # so we add service _lostServices to wait for device to arrive
                                #print 'Lost service:', entity.friendlyName
                                if entity.parentUDN not in self._lostServices.keys():
                                    self._lostServices[entity.parentUDN] = []
                                self._lostServices[entity.parentUDN].append(entity)
                            
                            #print entity
                            for handler in self.serviceFoundHandlers:
                                handler(data, entity)
                
                
                UDN = None
                if 'USN' in data.keys():                    
                    match = re.search('(uuid:[^:]*)', data['USN'])
                    UDN = match.group(1)
#                print 'LOCATION:', data['LOCATION']
#                if data['LOCATION'] not in self._cache.keys():
                #if UDN not in self._cache.keys():
                    #print UDN
                    #print self._cache.keys()
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
    
    def addDeviceHandler(self, handler):
        self.deviceFoundHandlers.append(handler)
            
    def removeDeviceHandler(self, handler):
        try: self.deviceFoundHandlers.remove(handler)
        except: pass
    
    def addServiceHandler(self, handler):
        self.serviceFoundHandlers.append(handler)
    
    def removeServiceHandler(self, handler):
        try: self.serviceFoundHandlers.remove(handler)
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

from lxml import etree
from xmlutil import genRootDesc

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
