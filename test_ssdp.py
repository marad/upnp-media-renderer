#!/usr/bin/python


# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
#from PyQt4.QtGui import QApplication, QWidget, QPushButton, QBoxLayout, QSizePolicy
#app = QApplication(sys.argv)
#import qt4reactor
#qt4reactor.install(app)
from twisted.internet import reactor
######################################################
    
from upnp.ssdp import Echo, SSDP

from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint

#from PyQt4.QtCore import SIGNAL, SLOT, Qt

class SSDPFactory(Factory):
    def buildProtocol(self, addr):
        return Echo()

def showProps(o, prefix=''):
    
    try:
        v = vars(o)
    except: 
        print prefix, v
        return
    
    for k, v in zip(v.keys(), v.values()):
        try:
            if isinstance(v, list):
                print prefix+'\t', k
                for object in v:
                    showProps(object, prefix=prefix+'\t\t')
            elif isinstance(v, dict):
                print prefix, k
                for key, value in zip(v.keys(), v.values()):
                    print prefix+'\t', key, ':'
                    showProps(value, prefix=prefix+'\t\t')
            else:
                print prefix, k, '=', v
        except Exception as e:
            print e
        
    
def deviceFoundHandler(headers, device):
    #print headers
    #print "Found device", device.friendlyName
    showProps(device)
    #for service in device.services:
    #    print service.serviceId, service.actions
    
if __name__ == "__main__":
    print "Testing SSDP..."
    
    ssdp = SSDP()
    ssdp.addHandler(deviceFoundHandler)
    ssdp.listen()
    ssdp.search(target='upnp:rootdevice')
    #ssdp.search()
    
#    widget = QWidget()
#    widget.setWindowTitle("SSDP Client/Server")
#    widget.setVisible(True)
#    
#    button = QPushButton("Zamknij")
#    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#    QWidget.connect(button, SIGNAL("clicked()"), app.quit)
#    
#    layout = QBoxLayout(QBoxLayout.TopToBottom)
#    layout.addWidget(button, 1)
#    widget.setLayout(layout)
    
    reactor.run() #@UndefinedVariable
    
    print "Zamykam aplikacje"