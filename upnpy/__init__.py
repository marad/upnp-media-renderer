
# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
from PyQt4.QtGui import QApplication
qtApp = QApplication(sys.argv)
import qt4reactor
qt4reactor.install(qtApp)
from twisted.internet import reactor
######################################################

print 'importing upnpy!'

__dict__ = ['discovery']

def run():
    from devman import DeviceManager
    from ssdp import SSDP
    
    global discovery, deviceManager;
    discovery = SSDP()
    discovery.listen()
    
    deviceManager = DeviceManager()
    
    reactor.run()         #@UndefinedVariable
    reactor.getThreadPool().stop()        #@UndefinedVariable