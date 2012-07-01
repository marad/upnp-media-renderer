'''
Created on 13-05-2012

@author: morti
'''

import upnpy
from upnpy.decorators import MyService
from upnpy.device import Service
from upnpy.xmlutil import LocalDeviceBuilder
from gui.player import Player

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QPushButton
from twisted.internet import reactor 

builder = LocalDeviceBuilder()

class ConnectionManager(Service):
    def __init__(self):
        Service.__init__(self)
        builder.serviceFromFile(
            "urn:schemas-upnp-org:service:ConnectionManager:1", 
            "urn:upnp-org:serviceId:ConnectionManager", 
            "xml/ConnectionManager.xml", self)
        
    def GetProtocolInfo(self): # 1
        return {
            "Source" : "",
            "Sink" : "http-get:*:*:*,http-get:*:audio/mpegurl:*,http-get:*:audio/mpeg:*,http-get:*:audio/mpeg3:*,http-get:*:audio/mp3:*,http-get:*:audio/mp4:*,http-get:*:audio/basic:*,http-get:*:audio/midi:*,http-get:*:audio/ulaw:*,http-get:*:audio/ogg:*,http-get:*:audio/DVI4:*,http-get:*:audio/G722:*,http-get:*:audio/G723:*,http-get:*:audio/G726-16:*,http-get:*:audio/G726-24:*,http-get:*:audio/G726-32:*,http-get:*:audio/G726-40:*,http-get:*:audio/G728:*,http-get:*:audio/G729:*,http-get:*:audio/G729D:*,http-get:*:audio/G729E:*,http-get:*:audio/GSM:*,http-get:*:audio/GSM-EFR:*,http-get:*:audio/L8:*,http-get:*:audio/L16:*,http-get:*:audio/LPC:*,http-get:*:audio/MPA:*,http-get:*:audio/PCMA:*,http-get:*:audio/PCMU:*,http-get:*:audio/QCELP:*,http-get:*:audio/RED:*,http-get:*:audio/VDVI:*,http-get:*:audio/ac3:*,http-get:*:audio/vorbis:*,http-get:*:audio/speex:*,http-get:*:audio/x-aiff:*,http-get:*:audio/x-pn-realaudio:*,http-get:*:audio/x-realaudio:*,http-get:*:audio/x-wav:*,http-get:*:audio/x-ms-wma:*,http-get:*:audio/x-mpegurl:*,http-get:*:application/x-shockwave-flash:*,http-get:*:application/ogg:*,http-get:*:application/sdp:*,http-get:*:image/gif:*,http-get:*:image/jpeg:*,http-get:*:image/ief:*,http-get:*:image/png:*,http-get:*:image/tiff:*,http-get:*:video/avi:*,http-get:*:video/mpeg:*,http-get:*:video/fli:*,http-get:*:video/flv:*,http-get:*:video/quicktime:*,http-get:*:video/vnd.vivo:*,http-get:*:video/vc1:*,http-get:*:video/ogg:*,http-get:*:video/mp4:*,http-get:*:video/BT656:*,http-get:*:video/CelB:*,http-get:*:video/JPEG:*,http-get:*:video/H261:*,http-get:*:video/H263:*,http-get:*:video/H263-1998:*,http-get:*:video/H263-2000:*,http-get:*:video/MPV:*,http-get:*:video/MP2T:*,http-get:*:video/MP1S:*,http-get:*:video/MP2P:*,http-get:*:video/BMPEG:*,http-get:*:video/x-ms-wmv:*,http-get:*:video/x-ms-avi:*,http-get:*:video/x-flv:*,http-get:*:video/x-fli:*,http-get:*:video/x-ms-asf:*,http-get:*:video/x-ms-asx:*,http-get:*:video/x-ms-wmx:*,http-get:*:video/x-ms-wvx:*,http-get:*:video/x-msvideo:*"
            }
    
    def GetCurrentConnectionIDs(self): 
        return {
            "ConnectionIDs": "0"
            }
    
    def GetCurrentConnectionInfo(self, ConnectionID):
        return {
            "Status": "Unknown",
            "Direction": "Input",
            "PeerConnectionID": "-1",
            "RcsID": "0",
            "AVTransportID": "0",
            "PeerConnectionManager": "/",
            "ProtocolInfo": "",
            }
        
        
class RenderingControl(Service):
    def __init__(self, player):
        Service.__init__(self)
        builder.serviceFromFile(
            "urn:schemas-upnp-org:service:RenderingControl:1",
            "urn:upnp-org:serviceId:RenderingControl",
            "xml/RenderingControl.xml", self)
        self.player = player
    
    def GetMute(self, InstanceID, Channel):
        return {
            "CurrentMute": self.player.getMute()
            }
    
    def SetMute(self, InstanceID, DesiredMute, Channel):        
        self.player.setMute(DesiredMute)
    
    def SelectPreset(self, InstanceID, PresetName):   
        pass
     
    def ListPresets(self, InstanceID):
        return {
            "CurrentPresetNameList": ""
            }
        
    def GetVolume(self, InstanceID, Channel): # 4
        return {
            "CurrentVolume": self.player.getVolume()
            }
        
    def SetVolume(self, InstanceID, DesiredVolume, Channel):
        print DesiredVolume
        self.player.setVolume(int(DesiredVolume))
    
class AVTransport(Service):
    def __init__(self, player):
        Service.__init__(self)
        self.player = player
        builder.serviceFromFile(
            "urn:schemas-upnp-org:service:AVTransport:1",
            "urn:upnp-org:serviceId:AVTransport",
            "xml/AVTransport.xml", self)
        self.uri = None
        self.nextURI = None
        self.nextURIMetaData = None
    
    def Play(self, InstanceID, Speed): # 6
        self.player.play()
    
    def Seek(self, InstanceID, Target, Unit):
        self.player.seek(Target, Unit)
    
    def Pause(self, InstanceID):
        self.player.pause()
    
    def Stop(self, InstanceID):
        self.player.stop()
        
    def Next(self, InstanceID):
        pass
    
    def Previous(self, InstanceID):
        pass
    
    def GetPositionInfo(self, InstanceID):
        
        pos = self.player.getPosition()
        tm = self.player.getTotalTime()
        return {
            "AbsTime": pos,
            "TrackDuration": tm,
            "TrackURI": self.uri,
            "AbsCount": "1",
            "Track": "1",
            "TrackMetaData": self.player.currentDIDL,
            "RelCount": "1",
            "RelTime": pos,
            }
        
    def GetMediaInfo(self, InstanceID): # 3
        return {
            "NextURI": self.nextURI,
            "CurrentURI": self.uri,
            "NextURIMetaData": self.nextURIMetaData,
            "RecordMedium": "NOT_IMPLEMENTED",
            "PlayMedium": "NONE",
            "NrTracks": "0",
            "WriteStatus": "NOT_IMPLEMENTED",
            "MediaDuration": self.player.getTotalTime(),
            "CurrentURIMetaData": self.player.currentDIDL,
            }
        
    def GetTransportInfo(self, InstanceID): # 2
        state = "STOPPED"
        
        if self.player.isPlaying():
            state = "PLAYING"
            
        return {
            "CurrentTransportState": state,
            "CurrentTransportStatus": "OK",
            "CurrentSpeed": "1",
            }
        
    def GetDeviceCapabilities(self, InstanceID):
        return {
            "RecQualityModes": "NONE,NETWORK,HDD,CD-DA,UNKNOWN",
            "RecMedia": "NOT_IMPLEMENTED",
            "PlayMedia": "NONE,NETWORK,HDD,UNKNOWN",
            }
        
    def GetTransportSettings(self, InstanceID):
        return {
            "RecQualityMode": "NOT_IMPLEMENTED",
            "PlayMode": "NORMAL",
            }
        
    def SetAVTransportURI(self, InstanceID, CurrentURIMetaData, CurrentURI): # 5
        print "URI Set:", CurrentURI
        self.uri = CurrentURI
        self.player.setCurrentSource(self.uri)
    
    def SetNextAVTransportURI(self, InstanceID, NextURI, NextURIMetaData):
        self.nextURI = NextURI
        self.nextURIMetaData = NextURIMetaData
        
if __name__ == '__main__':
    
    dev = builder.deviceFromFile("xml/renderer.xml", False)
    
    print "Device Name:", dev.friendlyName
    print "Device Type:", dev.deviceType
    print "Device UDN:", dev.UDN
    
    window = Player()
    window.show()
    
    devMan = upnpy.localDeviceManager
    
    dev.addService(ConnectionManager())
    dev.addService(RenderingControl(window.player))
    dev.addService(AVTransport(window.player))
    devMan.addDevice(dev)
    
    upnpy.run()
