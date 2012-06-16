#-*- coding: utf-8 -*-
"""
    This is simple SSDP implementation.
"""

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.web.resource import Resource
from twisted.internet import threads

from consts import USER_AGENT
from upnpy.xmlutil import XmlDescriptionBuilder
from threading import Lock
from upnpy.device import Device, Service
import os, re
import uuid
import socket
import traceback
import sys, time
from util import RegexUtil, Entity, localInterface

#from device import parseRootDeviceDesc

class SSDPUnicast(DatagramProtocol):
    packetHandler = None
    
    def __init__(self, ssdpPacketHandler):
        self.packetHandler = ssdpPacketHandler
    
    def datagramReceived(self, datagram, addr):
#        print "Unicast data!"
        self.packetHandler.datagramReceived(datagram, addr)

class SSDPMulticast(DatagramProtocol):
    packetHandler = None
    
    def __init__(self, ssdpPacketHandler):
        self.packetHandler = ssdpPacketHandler
    
    def datagramReceived(self, datagram, addr):
#        print "Multicast data!", datagram
        self.packetHandler.datagramReceived(datagram, addr)

     
#######################################################################################
#######################################################################################
   
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
    
    BYEBYE_DEV_TPL = 'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nNTS: ssdp:byebye\r\nUSN: %(uuid)s\r\nNT: %(nt)s\r\n\r\n'
    BYEBYE_SRV_TPL = 'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nNTS: ssdp:byebye\r\nUSN: %(uuid)s::%(nt)s\r\nNT: %(nt)s\r\n\r\n'
    
    def __init__(self):
        self._cache = {}
        self._lostDevices = {}
        self._lostServices = {}        
        self._localDevices = {}
        self.deviceFoundHandlers = []
        self.serviceFoundHandlers = []
        self.deviceExpiredHandlers = []
        self.xmlParser = XmlDescriptionBuilder()
        
    def listen(self):
        self.unicast = reactor.listenUDP(0, SSDPUnicast(self)) #@UndefinedVariable
        self.multicast = reactor.listenMulticast(self.SSDP_PORT, SSDPMulticast(self), #@UndefinedVariable
                                                 listenMultiple = True)
        self.multicast.setTTL(5)
        self.multicast.joinGroup(self.SSDP_ADDR)

            
        #self.descServer = reactor.listenTCP(0, Site(DescriptionServerPage(self))) #@UndefinedVariable
        self.descServer = upnpy.descServer
        self._removeOldDevices()
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
            
            if data['TYPE'] == SSDP.TYPE_SEARCH:
                #searchDevice = str(data['ST'])
                #if searchDevice.startswith("uuid:"):
                #    self.unicast.write(TPL % (device.deviceType, device.UDN+"::"+device.deviceType), addr)
                upnpy.localDeviceManager.searchResponse(data, addr)
            
            UDN = None    
            if 'USN' in data.keys():      
                UDN = RegexUtil.getUUID(data['USN'])
                
            # Check if we've found new device
            if 'LOCATION' in data.keys() and UDN not in self._cache.keys():
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
                            
                            # save server info
                            info = RegexUtil.getServerAndPortFromURL(data['LOCATION'])
                            serverInfo = Entity()
                            serverInfo.address = info[0]
                            serverInfo.port = info[1]
                            entity.serverInfo = serverInfo
                            
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
                
                
                #UDN = None
                #if 'USN' in data.keys():                    
                #    match = re.search('(uuid:[^:]*)', data['USN'])
                #    UDN = match.group(1)
#                print 'LOCATION:', data['LOCATION']
#                if data['LOCATION'] not in self._cache.keys():
                #if UDN not in self._cache.keys():
                    #print UDN
                    #print self._cache.keys()
                threads.deferToThread(inner_parseDeviceInfo).addCallback(inner_resultCallBack)
            
            
            # Refresh age information
            if 'CACHE-CONTROL' in data.keys() and UDN in self._cache.keys() and data['CACHE-CONTROL']:
                maxAge = RegexUtil.getMaxAge(data['CACHE-CONTROL']);
                self._cache[UDN].maxAge = time.time() + maxAge
                #print self._cache[UDN].maxAge
                
                                               
        except:
            traceback.print_exc()
            
        
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
    
    def alive(self, device, maxAge=1800, spreadInTime=True, spreadSpan=30, addr=None):
        
        # TODO: poprawic aby uruchamial sie watek i rozkladal 
        # komunikaty rownomiernie w czasie
        #print self.descServer.getHost().host
        #print device
        
        if addr is None:
            addr = (self.SSDP_ADDR, self.SSDP_PORT)        
        
        path = '/device/%s.xml' % device.UDN
        baseURL = upnpy.descServer.getBaseURL()
        rootDescURL = "%s%s" % (upnpy.descServer.getBaseURL(), path)        
        device.rootDescURL = rootDescURL
        device.baseURL = baseURL
        
        TPL = self.NOTIFY_TPL % (maxAge, rootDescURL, "%s", USER_AGENT, "%s")
        
        self.unicast.write(TPL % ("upnp:rootdevice", device.UDN+"::"+device.deviceType), addr)
        self.unicast.write(TPL % (device.deviceType, device.UDN+"::"+device.deviceType), addr)
        self.unicast.write(TPL % (device.UDN, device.UDN+"::"+device.deviceType), addr)
        
        # TODO: notify about subdevices
        #for device in device.devices.values():
        #    self.unicast.write(TPL % (service.serviceType, device.UDN+"::"+service.serviceType), addr)
            
        for service in device.services.values():
            service.SCPDURL = upnpy.descServer.getSCPDURL(service)
            service.controlURL = upnpy.descServer.getControlURL(service)
            service.eventSubURL = upnpy.descServer.getEventSubURL(service)            
            self.unicast.write(TPL % (service.serviceType, device.UDN+"::"+service.serviceType), addr)
        
        #data = self.NOTIFY_TPL % (maxAge, rootDescURL, device.deviceType, USER_AGENT, 
#                                 device.UDN+"::"+device.deviceType)
#        self.unicast.write(data, (self.SSDP_ADDR, self.SSDP_PORT))
        
#        data = self.NOTIFY_TPL % (maxAge, rootDescURL, "upnp:rootdevice", USER_AGENT, 
#                                 device.UDN+"::"+device.deviceType)
#        self.unicast.write(data, (self.SSDP_ADDR, self.SSDP_PORT))

    def byeDevice(self, device):
        self.alive(device, maxAge=0)
        rotmsg = self.BYEBYE_SRV_TPL % {'nt': "upnp:rootdevice", 'uuid': device.UDN}
        msg = self.BYEBYE_SRV_TPL % {'nt': device.deviceType, 'uuid': device.UDN}
        devmsg = self.BYEBYE_DEV_TPL % {'nt': device.UDN, 'uuid': device.UDN}
        
        if not device.embedded:
            self.unicast.write(rotmsg, (self.SSDP_ADDR, self.SSDP_PORT))
        self.unicast.write(msg, (self.SSDP_ADDR, self.SSDP_PORT))
        
        for dev in device.devices.values():
            self.byeDevice(dev)
        
        for srv in device.services.values():
            self.byeService(srv)
            
        self.unicast.write(devmsg, (self.SSDP_ADDR, self.SSDP_PORT))
        
            
    def byeService(self, service):
        msg = self.BYEBYE_SRV_TPL % {'nt': service.serviceType, 'uuid': service.device.UDN}
        self.unicast.write(msg, (self.SSDP_ADDR, self.SSDP_PORT))
    
    def byeBye(self, deviceOrService):
        print "Bye ", deviceOrService
        msg = None
        if isinstance(deviceOrService, Device):
            self.byeDevice(deviceOrService)
#            print "Removing device"
#            msg = self.BYEBYE_SRV_TPL % {'nt': deviceOrService.deviceType, 'uuid': deviceOrService.UDN}
#            if not deviceOrService.embedded:
#                rotmsg = self.BYEBYE_SRV_TPL % {'nt': "upnp:rootdevice", 'uuid': deviceOrService.UDN}
#                self.unicast.write(rotmsg, (self.SSDP_ADDR, self.SSDP_PORT))
#                
#            devmsg = self.BYEBYE_DEV_TPL % {'nt': deviceOrService.UDN, 'uuid': deviceOrService.UDN}
#            self.unicast.write(rotmsg, (self.SSDP_ADDR, self.SSDP_PORT))
#            
#            for srv in deviceOrService.services.values():
#                self.byeBye(srv)
            
        
        elif isinstance(deviceOrService, Service):
            self.byeService(deviceOrService)
#            msg = self.BYEBYE_SRV_TPL % {'nt': deviceOrService.serviceType, 'uuid': deviceOrService.device.UDN}
        
#        if msg is None: return
#        else:
#            self.unicast.write(msg, (self.SSDP_ADDR, self.SSDP_PORT))
        
    
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
        
    def addDeviceExpiredHandler(self, handler):
        self.deviceExpiredHandlers.append(handler)
    
    def removeDeviceExpiredHandler(self, handler):
        try: self.deviceExpiredHandlers.remove(handler)
        except: pass
        
    def _removeOldDevices(self):
        toRemove = []
        t = time.time()
        for udn, dev in self._cache.iteritems():
            try:
                if t > dev.maxAge:
                    toRemove.append(udn)
            except:
                traceback.print_exc()
        
        def removeDevice(device):
            for subDev in device.devices:
                removeDevice(subDev)
                
            for handler in self.deviceExpiredHandlers:
                handler(device)            
            del self._cache[device.UDN]
            
        for udn in toRemove:            
            #print '===== REMOVING DEVICE', self._cache[udn].friendlyName, '! ====='
            removeDevice(self._cache[udn])
            #del self._cache[udn]
            
        reactor.callLater(10.5, self._removeOldDevices) #@UndefinedVariable
        
    def _genUUID(self, name):
        return uuid.uuid5(uuid.NAMESPACE_URL, name)
    
    
    @property
    def devices(self):
        return self._cache.values()
    
    @property
    def localDevices(self):
        return self._localDevices.values()
        
        
    


#######################################################################################
#######################################################################################
       

from lxml import etree
from xmlutil import genRootDesc
import upnpy

class DescriptionServerPage(Resource):
    isLeaf = True
    def __init__(self):
        self.ssdp = upnpy.discovery
        self.localDevices = upnpy.localDeviceManager
        
    def render_GET(self, request):
        print 'Desc server got request:', request.path
        
        match = re.search('/([^/]+)/([^.]+).xml', request.path)
        if match == None:
            return "ERROR"
        
        resType = match.group(1)
        resId = match.group(2)
                
        
        if resType == 'device':
            request.responseHeaders.setRawHeaders('content-type', ['text/xml'])            
            device = self.localDevices.getDevice(resId)
            print etree.tostring(genRootDesc(device))
            return etree.tostring(genRootDesc(device))
    
        if resType == 'service':
            request.responseHeaders.setRawHeaders('content-type', ['text/xml'])
            
            for device in self.ssdp._localDevices.values():
                if resId in device.services.keys():
                    service = device.services[resId]
                    return etree.tostring(service.genSCPD())
                    
        return "NUTHING"
    
    def getSCPDURL(self, service):
        if service.device:
            return  "/%s::%s" % (service.device.UDN, service.serviceId)
        else:
            return None
    
    def getControlUrl(self, service):
        if service.device:
            return             
        else:
            return None