#-*- coding: utf-8 -*-
"""
    This is simple SSDP implementation.
"""

from twisted.internet.protocol import DatagramProtocol
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import uuid

#from device import parseRootDeviceDesc
from upnp.parser import DeviceDescriptionParser

class Echo(Protocol):
    def dataReceived(self, data):
        self.transport.write(data)
        
    def connectionMade(self):
        print "Podłączył się klient..."
            
    def connectionLost(self, reason):
        print "Klient się rozłączył..."
        print "Powód: " + str(reason) 

class Object:
    pass
        
class SSDP(DatagramProtocol):
    
    SSDP_PORT = 1900
    SSDP_ADDR = "239.255.255.250"
    INADDR_ANY = "0.0.0.0"
    
    TYPE_OK = 0
    TYPE_NOTIFY = 1
    TYPE_SEARCH = 2
    
    
    def __init__(self):
        self.deviceFoundHandlers = []
        self.descriptionParser = DeviceDescriptionParser()
        
    def listen(self):
        self.multicast = reactor.listenMulticast(self.SSDP_PORT, self, #@UndefinedVariable
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
            
            if data['type'] == SSDP.TYPE_OK and data['ST'] == "upnp:rootdevice":
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
            
        
    def search(self, target='ssdp:all', mx=3):
        msg = 'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: %s\r\nST: %s\r\n\r\n' % (mx, target)
        self.transport.write(msg, (self.SSDP_ADDR, self.SSDP_PORT))
        
        #msg = 'M-SEARCH * HTTP/1.1\r\nHOST: 192.168.0.114:1900\r\nMAN: "ssdp:discover"\r\nMX: %s\r\nST: %s\r\n\r\n' % (mx, target)
        #self.transport.write(msg, ('192.168.0.114', self.SSDP_PORT))
        #self.transport.write(msg, ('127.0.0.1', self.SSDP_PORT))
    
    def addHandler(self, handler):
        self.deviceFoundHandlers.append(handler)
            
    def removeHandler(self, handler):
        try: self.deviceFoundHandlers.remove(handler)
        except: pass
        
    def _genUUID(self, name):
        return uuid.uuid5(uuid.NAMESPACE_URL, name)
