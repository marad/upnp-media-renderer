
# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
from PyQt4.QtGui import QApplication
qtApp = QApplication(sys.argv)
import qt4reactor
qt4reactor.install(qtApp)
from twisted.internet import reactor
######################################################

module = sys.modules[__name__]

from devman import RemoteDeviceManager, LocalDeviceManager
from ssdp import SSDP, DescriptionServerPage
from description import DescriptionServer

module.qtApp = qtApp
 
module.discovery = SSDP()
module.remoteDeviceManager = RemoteDeviceManager()    
module.localDeviceManager = LocalDeviceManager()
module.descServer = DescriptionServer()

def run(runSearch=True):
    
    #module.descServer = reactor.listenTCP(0, Site(DescriptionServerPage())) #@UndefinedVariable
    module.descServer.listen()
    module.discovery.listen()
    
    if runSearch:
        module.discovery.search()
    
    module.localDeviceManager._sendAlive()
    
    reactor.run()                   #@UndefinedVariable
    reactor.getThreadPool().stop()  #@UndefinedVariable