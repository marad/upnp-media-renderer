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
            "Sink" : "http-get:*:*:*,xbmc-get:*:*:*,http-get:*:audio/mpegurl:*,http-get:*:audio/mpeg:*,http-get:*:audio/mpeg3:*,http-get:*:audio/mp3:*,http-get:*:audio/mp4:*,http-get:*:audio/basic:*,http-get:*:audio/midi:*,http-get:*:audio/ulaw:*,http-get:*:audio/ogg:*,http-get:*:audio/DVI4:*,http-get:*:audio/G722:*,http-get:*:audio/G723:*,http-get:*:audio/G726-16:*,http-get:*:audio/G726-24:*,http-get:*:audio/G726-32:*,http-get:*:audio/G726-40:*,http-get:*:audio/G728:*,http-get:*:audio/G729:*,http-get:*:audio/G729D:*,http-get:*:audio/G729E:*,http-get:*:audio/GSM:*,http-get:*:audio/GSM-EFR:*,http-get:*:audio/L8:*,http-get:*:audio/L16:*,http-get:*:audio/LPC:*,http-get:*:audio/MPA:*,http-get:*:audio/PCMA:*,http-get:*:audio/PCMU:*,http-get:*:audio/QCELP:*,http-get:*:audio/RED:*,http-get:*:audio/VDVI:*,http-get:*:audio/ac3:*,http-get:*:audio/vorbis:*,http-get:*:audio/speex:*,http-get:*:audio/x-aiff:*,http-get:*:audio/x-pn-realaudio:*,http-get:*:audio/x-realaudio:*,http-get:*:audio/x-wav:*,http-get:*:audio/x-ms-wma:*,http-get:*:audio/x-mpegurl:*,http-get:*:application/x-shockwave-flash:*,http-get:*:application/ogg:*,http-get:*:application/sdp:*,http-get:*:image/gif:*,http-get:*:image/jpeg:*,http-get:*:image/ief:*,http-get:*:image/png:*,http-get:*:image/tiff:*,http-get:*:video/avi:*,http-get:*:video/mpeg:*,http-get:*:video/fli:*,http-get:*:video/flv:*,http-get:*:video/quicktime:*,http-get:*:video/vnd.vivo:*,http-get:*:video/vc1:*,http-get:*:video/ogg:*,http-get:*:video/mp4:*,http-get:*:video/BT656:*,http-get:*:video/CelB:*,http-get:*:video/JPEG:*,http-get:*:video/H261:*,http-get:*:video/H263:*,http-get:*:video/H263-1998:*,http-get:*:video/H263-2000:*,http-get:*:video/MPV:*,http-get:*:video/MP2T:*,http-get:*:video/MP1S:*,http-get:*:video/MP2P:*,http-get:*:video/BMPEG:*,http-get:*:video/x-ms-wmv:*,http-get:*:video/x-ms-avi:*,http-get:*:video/x-flv:*,http-get:*:video/x-fli:*,http-get:*:video/x-ms-asf:*,http-get:*:video/x-ms-asx:*,http-get:*:video/x-ms-wmx:*,http-get:*:video/x-ms-wvx:*,http-get:*:video/x-msvideo:*"
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
    def __init__(self):
        Service.__init__(self)
        builder.serviceFromFile(
            "urn:schemas-upnp-org:service:RenderingControl:1",
            "urn:upnp-org:serviceId:RenderingControl",
            "xml/RenderingControl.xml", self)
    
    def GetMute(self, InstanceID, Channel):
        return {
            "CurrentMute": "0"
            }
    
    def SetMute(self, InstanceID, DesiredMute, Channel):
        pass
    
    def SelectPreset(self, InstanceID, PresetName):   
        pass
     
    def ListPresets(self, InstanceID):
        return {
            "CurrentPresetNameList": ""
            }
        
    def GetVolume(self, InstanceID, Channel): # 4
        return {
            "CurrentVolume": "100"
            }
        
    def SetVolume(self, InstanceID, DesiredVolume, Channel):
        pass
    
class AVTransport(Service):
    def __init__(self, player):
        Service.__init__(self)
        self.player = player
        builder.serviceFromFile(
            "urn:schemas-upnp-org:service:AVTransport:1",
            "urn:upnp-org:serviceId:AVTransport",
            "xml/AVTransport.xml", self)
    
    
    def Play(self, InstanceID, Speed): # 6
        print 'Playing', self.uri
        self.player.play(self.uri)
    
    def Seek(self, InstanceID, Target, Unit):
        print Target, Unit
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
        return {
            "AbsTime": "00:00:00",
            "TrackDuration": "00:00:00",
            "TrackURI": self.uri,
            "AbsCount": "1",
            "Track": "1",
            "TrackMetaData": '<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/"><item id="29" parentID="8" restricted="1"><upnp:class>object.item.videoItem</upnp:class><dc:title>Track Metadata :)</dc:title><dc:creator>Dummy Data</dc:creator><upnp:artist>Unknown Artist</upnp:artist><upnp:album>Unknown Album</upnp:album><res protocolInfo="http-get:*:video/x-flv:*" bitrate="378" sampleFrequency="44100" duration="0:05:15.000">http://www.wp.pl/</res></item></DIDL-Lite>',
            "RelCount": "1",
            "RelTime": "",
            }
        
    def GetMediaInfo(self, InstanceID): # 3
        return {
            "NextURI": "NOT_IMPLEMENTED",
            "CurrentURI": self.uri,
            "NextURIMetaData": "NOT_IMPLEMENTED",
            "RecordMedium": "NOT_IMPLEMENTED",
            "PlayMedium": "NONE",
            "NrTracks": "0",
            "WriteStatus": "NOT_IMPLEMENTED",
            "MediaDuration": "00:00:00",
            "CurrentURIMetaData": "",
            }
        
    def GetTransportInfo(self, InstanceID): # 2
        state = "STOPPED"
        
        if self.player.player.isPlaying():
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
            "PlayMedia": "NOT_IMPLEMENTED",
            }
        
    def GetTransportSettings(self, InstanceID):
        return {
            "RecQualityMode": "NOT_IMPLEMENTED",
            "PlayMode": "NORMAL",
            }
        
    def SetAVTransportURI(self, InstanceID, CurrentURIMetaData, CurrentURI): # 5
        print "URI Set:", CurrentURI
        self.uri = CurrentURI
        
        
if __name__ == '__main__':
    
    dev = builder.deviceFromFile("xml/renderer.xml", False)
    
    #print dir(dev)
    print dev.friendlyName
    print dev.deviceType
    print dev.UDN
    
    window = Player()
    window.show()
    
    #btn = QPushButton('CLOSE')
    #QPushButton.connect(btn, SIGNAL("clicked()"), upnpy.localDeviceManager.byeBye)
    #btn.show()
    
    devs = upnpy.localDeviceManager
    
    print dev
    srv = MyService()
    srv.serviceType = 'urn:schemas-upnp-org:service:MyService:1'
    srv.serviceId = 'AddService'
    dev.addService(srv)
    dev.addService(ConnectionManager())
    dev.addService(RenderingControl())
    dev.addService(AVTransport(window))
    devs.addDevice(dev)
    
    upnpy.run()