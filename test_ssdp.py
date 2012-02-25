#!/usr/bin/python


# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
from PyQt4.QtGui import QApplication, QWidget, QPushButton, QBoxLayout, QSizePolicy
app = QApplication(sys.argv)
import qt4reactor
qt4reactor.install(app)
from twisted.internet import reactor
######################################################
    
from upnpy.ssdp import SSDP
from upnpy.soap import SOAPClient
from upnpy.controller import ControllerFactory

from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint

from PyQt4.QtGui import QTextEdit
from PyQt4.QtCore import SIGNAL, SLOT, Qt

global edit
edit = QTextEdit()

ssdp = SSDP()


def log(text):
    global edit
    edit.setText(edit.toPlainText() + text + "\r\n")
    
def showProps(o, prefix=''):
    
    try:
        v = vars(o)
    except: 
        log( prefix + repr(o) )
        return
    
    for k, v in zip(v.keys(), v.values()):
        try:
            if isinstance(v, list):
                log (prefix+ '\t'+ k)
                for object in v:
                    showProps(object, prefix=prefix+'\t\t')
            elif isinstance(v, dict):
                log(prefix + k)
                for key, value in zip(v.keys(), v.values()):
                    log(prefix+'\t'+key+ ':')
                    showProps(value, prefix=prefix+'\t\t')
            else:
                log( prefix + k + ' = ' + v )
        except Exception as e:
            #print e
            pass
        
    
def deviceFoundHandler(headers, device):
    log("Found device: " + device.deviceType) # + "(" + device.UDN + ")")
    
    if device.friendlyName == "GUPnP Network Light":
        
        service = device.services.values()[1]
        #print service
        action = service.actions.values()[0]
    
        print service.serviceType
        print service.host
        print service.port
    
        soap = SOAP()
        
        print soap.invokeActionByName(service, "SetTarget",
                          {'NewTargetValue':'false'})
    
        #log( soap._genRequest('router:1780', service, action) )
    
        #log('\r\n\r\n\r\n')
    
        #log( soap._genResponse(service, action) )
    
    #ssdp.alive(device)
    
    #print headers
    #print "Found device", device.friendlyName
    #print "It has subdevices: " 
    #for name in device.devices.values():
    #    print "\t", name.friendlyName
    
    #showProps(device)
    #for service in device.services:
    #    print service.serviceId, service.actions
    
def search():
    global edit
    edit.setText("")
    ssdp.search(target="upnp:rootdevice", mx=1)

if __name__ == "__main__":
    print "Testing SSDP..."
    
    #factory = ControllerFactory()
    #reactor.connectTCP('router', 1780, factory) #@UndefinedVariable
        
    ssdp.addHandler(deviceFoundHandler)
    ssdp.listen()
    #ssdp.search(target='upnp:rootdevice', mx=1)
    #ssdp.search()    
    #ssdp.search(target='urn:schemas-upnp-org:service:SwitchPower:1')
    ssdp.search(target='urn:schemas-upnp-org:device:DimmableLight:1')
    #ssdp.search(target='urn:schemas-upnp-org:device:InternetGatewayDevice:1')
    
    #ssdp.search()
    #ssdp.search(addr=('192.168.0.114', 1900))
    
    widget = QWidget()
    widget.setWindowTitle("SSDP Client/Server")
    widget.setVisible(True)
    
    closeButton = QPushButton("Zamknij")
    closeButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    QWidget.connect(closeButton, SIGNAL("clicked()"), app.quit)
    
    searchButton = QPushButton("Search")
    QWidget.connect(searchButton, SIGNAL("clicked()"), search)
    
    global edit
    edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)    
    
    layout = QBoxLayout(QBoxLayout.TopToBottom)
    layout.addWidget(edit, 3)
    layout.addWidget(searchButton)
    layout.addWidget(closeButton)
    widget.setLayout(layout)
        
    
    reactor.run() #@UndefinedVariable
    
    print "Zamykam aplikacje"