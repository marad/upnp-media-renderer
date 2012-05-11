'''
Created on 25-02-2012

@author: morti
'''

from upnpy.ssdp import SSDP


class DeviceManager(object):
    
    def __init__(self):
        self.ssdp = SSDP()   
        self.soapServer = None # TODO: create SOAPServer implementation
        self._localDevices = {}
        
        self._remoteDevices = {}
        self._lostRemoteServices = {}
        
    
    def foundRemoteDevice(self, headers, device):
        pass
    
    def foundRemoteService(self, headers, service):
        pass
    
    #def addRemoteDevice(self, device):
    #    pass
    
    def addLocalDevice(self, device):
        pass
    
    @property
    def devices(self):
        return self.ssdp.devices
    
    @property
    def localDevices(self):
        return self._localDevices.values()
    