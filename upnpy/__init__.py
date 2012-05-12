
# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
from PyQt4.QtGui import QApplication
qtApp = QApplication(sys.argv)
import qt4reactor
qt4reactor.install(qtApp)
from twisted.internet import reactor
######################################################

print 'importing upnpy!'

def run():
    from devman import DeviceManager
    from ssdp import SSDP
    
    if 'upnpy.discovery' not in sys.modules:
        discovery = SSDP()
        discovery.listen()
        sys.modules['upnpy.discovery'] = discovery    
    
    if 'upnpy.deviceManager' not in sys.modules:
         sys.modules['upnpy.deviceManager'] = DeviceManager()
    
    reactor.run()         #@UndefinedVariable
    reactor.getThreadPool().stop()        #@UndefinedVariable