'''
Created on 25-02-2012

@author: morti
'''

import upnpy, re, copy, socket
from twisted.internet import reactor

class LocalDeviceManager(object):
    def __init__(self):
        self.ssdp = upnpy.discovery
        
        self._devices = {}
    
    def _sendAliveForDevice(self, device, addr=None):
        self.ssdp.alive(device, maxAge=15, addr=addr)
    
    def _sendAlive(self, addr=None):
        # TODO: send alive message
        for device in self._devices.values():
            self._sendAliveForDevice(device, addr)            
        
        reactor.callLater(10, self._sendAlive) #@UndefinedVariable
    
    def getDevice(self, uuid):
        return self._devices[uuid]
    
    def addDevice(self, device):
        if device.UDN not in self._devices.keys():
            try:
                self._devices[device.UDN] = device
                self._sendAliveForDevice(device)
            except: pass
    
    def removeDevice(self, device):
        self.ssdp.byeBye(device)
        del self._devices[device.UDN]
    
    def searchResponse(self, headers, addr):        
        self._sendAlive(addr)
    
    def byeBye(self):
        print 'HELO'
        for dev in self._devices:
            self.ssdp.byeBye(dev)

class RemoteDeviceManager(object):
    
    NEW         = "NEW"
    UPDATED     = "UPDATED"
    REMOVED     = "REMOVED"
    
    def __init__(self):
        self.ssdp = upnpy.discovery 
        
        self.ssdp.addDeviceHandler(self.foundRemoteDevice)
        self.ssdp.addServiceHandler(self.foundRemoteService)
        self.ssdp.addDeviceExpiredHandler(self.remoteDeviceExpired)
        
        self._remoteDevices = {}
        self._lostRemoteServices = {}
        self._lostRemoteSubdevices = {}
        
        self._callbacks = []
        self._remoteCallbacks = []  
    
    def foundRemoteDevice(self, headers, device):        
        # Attach services
        try:
            services = self._lostRemoteServices[device.UDN]
            for service in services:
                device.addService(service)
            del self._lostRemoteServices[device.UDN]
        except: pass
        
        # Attach embedded devices
        try:
            devices = self._lostRemoteSubdevices[device.UDN]
            for dev in devices:
                device.addDevice(dev)
            del self._lostRemoteSubdevices[device.UDN]
        except: pass
    
        # Put into device dictionary
        self._remoteDevices[device.UDN] = device
        self._notify(device, False)
        
        # If embedded - add to parent device
        if device.embedded:
            if device.parentUDN not in self._remoteDevices.keys():
                if device.parentUDN not in self._lostRemoteSubdevices.keys():
                    self._lostRemoteSubdevices = []
                self._lostRemoteSubdevices.append(device)
            else:
                self._remoteDevices[device.parentUDN].addDevice(device)
                self._notify(self._remoteDevices[device.parentUDN], False)
            

    def foundRemoteService(self, headers, service):
        #print 'Remote service!', service
        try:
            # Add service to device
            self._remoteDevices[service.parentUDN].addService(service)
            self._notify(self._remoteDevices[service.parentUDN ], True)
        except:
            # Or put it in lost services container to wait for device
            if service.parentUDN not in self._lostRemoteServices.keys():
                self._lostRemoteServices[service.parentUDN] = []
            self._lostRemoteServices[service.parentUDN].append(service)
            
    def remoteDeviceExpired(self, device):
        #print 'Remove device:', device.friendlyName
        self._notify(device, False, True)
            
    # Registers callback when device need attention (new or updated).
    # @param callback: Callback function to call. It has to have two parameters: device and state. 
    # @param typeFilter: String containing regexp that filters the devices by type. 
    #    Only devices with matching type will activate the callback. Default = None = All devices
    # @param userFilterCallback: Filter callback function that receives device as argument
    #    and returns boolean value. If returned value is True then notification is going to be sent.
    #    If type filter is also specified it will be checked first and then (if it accepted device)
    #    filter callback is executed.
    def addDeviceCallback(self, callback, typeFilter=None, userFilterCallback=None):
        if typeFilter:
            regexp = re.compile(typeFilter)
        else:
            regexp = None
            
        self._callbacks.append( (callback, regexp, userFilterCallback) )
        
        for dev in self._remoteDevices:
            if self._filter(dev, regexp, userFilterCallback):
                self._notify(dev)
    
    def _filter(self, device, typeFilter, userFilter):
        
        match = True
        if typeFilter:
            match = typeFilter.match(device.deviceType)

        user = True   
        if userFilter:
            user = userFilter(device)
        
        return match and user
    
    def _notify(self, device, update=False, remove=False):
        state = self.NEW
        if update:
            state = self.UPDATED
            
        if remove:
            state = self.REMOVED
            
        for callback, typeFilter, userFilter in self._callbacks:
            if self._filter(device, typeFilter, userFilter):
                callback(device, state)
                
    def getDevices(self, typeFilter=None, userFilterCallback=None):        
        return [x for x in self._remoteDevices if self._filter(x, typeFilter, userFilterCallback)]
        
    @property
    def devices(self):
        return copy.deepcopy( self._remoteDevices )
    
    @property
    def rootDevices(self):
        return [x for x in self._remoteDevices if not hasattr(x, 'parentUDN')]
    
    