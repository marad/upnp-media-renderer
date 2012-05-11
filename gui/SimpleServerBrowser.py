'''
Created on 08-05-2012

@author: morti
'''

from upnpy.ssdp import SSDP
from upnpy.soap import SOAPClient

from PyQt4.QtGui import QWidget, QBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QTextEdit
from PyQt4.QtGui import QPushButton, QGroupBox, QLineEdit, QMessageBox
from PyQt4.QtCore import SIGNAL

class SimpleServerBrowser(QWidget):
    '''
    classdocs
    '''

    def __init__(self, parent = None):
        '''
        Constructor
        '''
        QWidget.__init__(self, parent = parent)
        
        self.devices = []
        self.servers = []
        self.unmachedServices = []
        
        self.ssdp = SSDP();
        self.soap = SOAPClient();
    
        self.ssdp.addDeviceHandler(self.addDevice)
        self.ssdp.addServiceHandler(self.addService);
        self.ssdp.listen()
        self.ssdp.search()
        
    def addDevice(self, headers, device):
        print 'Found device:', device.friendlyName
    
    def addService(self, headers, service):
        print 'Found service', service.friendlyName, 'for device', service.parentUDN
        