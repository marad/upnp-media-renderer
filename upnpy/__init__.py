
# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
from PyQt4.QtGui import QApplication
qtApp = QApplication(sys.argv)
import qt4reactor
qt4reactor.install(qtApp)
from twisted.internet import reactor
######################################################

module = sys.modules[__name__]

from devman import RemoteDeviceManager
from ssdp import SSDP

module.qtApp = qtApp

module.ssdp = SSDP()
module.remoteDeviceManager = RemoteDeviceManager()    

def run():
    module.ssdp.listen()
    module.ssdp.search()
    
    reactor.run()         #@UndefinedVariable
    reactor.getThreadPool().stop()        #@UndefinedVariable