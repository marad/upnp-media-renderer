#-*- coding: utf-8 -*-
"""
    This is simple SSDP implementation.
"""

from twisted.internet.protocol import DatagramProtocol
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import os,  uuid

#from device import parseRootDeviceDesc
from upnpy.parser import DeviceDescriptionParser
from upnpy import USER_AGENT

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

        
class SSDP(DatagramProtocol):
    
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
        self.deviceFoundHandlers = []
        self.descriptionParser = DeviceDescriptionParser()
        
    def listen(self):
        self.unicast = reactor.listenUDP(0, SSDPUnicast(self)) #@UndefinedVariable
        self.multicast = reactor.listenMulticast(self.SSDP_PORT, SSDPMulticast(self), #@UndefinedVariable
                                                 listenMultiple = True)
        self.multicast.setTTL(5)
        self.multicast.joinGroup(self.SSDP_ADDR)
        
    def startProtocol(self):
        pass
        
    
    def datagramReceived(self, datagram, addr):
        lines = datagram.strip().split('\r\n')
        #print "Server received: ", repr(addr), lines
        

        try:        
            data = {}
            data['type'] = None        
            
            if '200 OK' in lines[0].upper():
                data['type'] = SSDP.TYPE_OK
            elif 'NOTIFY' in lines[0].upper():
                data['type'] = SSDP.TYPE_NOTIFY
            elif 'M-SEARCH' in lines[0].upper():
                data['type'] = SSDP.TYPE_SEARCH
                
            del lines[0]
    
            for field in lines:
                if ':' in field:
                    name, value = field.split(':', 1)
                    name, value = [name.strip().upper(), value.strip()]
                    data[name] = value
            
            print addr, data
            
            # Check if we've found the device
            if 'LOCATION' in data.keys():
                
                try: # Try to parse the device XML           
                    #device = parseRootDeviceDesc(data)
                    device = self.descriptionParser.parse(data)
                    for handler in self.deviceFoundHandlers:
                        handler(data, device)
                except Exception as e: # But if you cant
                    import traceback
                    import sys
                    traceback.print_exc(file=sys.stderr)
                    print e
                
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
    
    def alive(self, device, maxAge=1800):
        print self.NOTIFY_TPL % (maxAge, device.rootDescURL, device.deviceType, USER_AGENT, 
                                 device.UDN+"::"+device.deviceType)
        pass
    
    def addHandler(self, handler):
        self.deviceFoundHandlers.append(handler)
            
    def removeHandler(self, handler):
        try: self.deviceFoundHandlers.remove(handler)
        except: pass
        
    def _genUUID(self, name):
        return uuid.uuid5(uuid.NAMESPACE_URL, name)
    