'''
Created on 08-05-2012

@author: morti
'''

import upnpy
from upnpy.soap import SOAPClient
from upnpy.xmlutil import DIDLParser
#from gui.video import VideoPlayer

from PyQt4.QtGui import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QTextEdit
from PyQt4.QtGui import QPushButton, QGroupBox, QLineEdit, QMessageBox, QComboBox
from PyQt4.QtCore import SIGNAL, QAbstractListModel, Qt, QModelIndex, QVariant


class ServerListModel(QAbstractListModel):
    def __init__(self):
        QAbstractListModel.__init__(self)
        self.data = []
        upnpy.remoteDeviceManager.addDeviceCallback(self._deviceStatus, ".*MediaServer.*")
    
    def data(self, index, role):        
        if index.row() == 0:
            return 'Wybierz serwer...'
        else:
            dev = self.data[index.row()-1]
            return "%s (%s)" % (dev.friendlyName, dev.serverInfo.address) 

    def headerData(self, section, orientation, role):
        pass
    
    def rowCount(self, parentIndex):
        return len(self.data) + 1

    def addItem(self, device):
        self.data.append(device)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), 
            self.index(len(self.data), 0), 
            self.index(len(self.data), 0))
    
    def removeItem(self, device):
        idx = self.data.index(device)
        self.data.remove(device)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), 
            self.index(idx, 0), 
            self.index(idx, 0))
    
    def _deviceStatus(self, device, status):        
        if status == "NEW":
            self.addItem(device)
        elif status == "REMOVED":
            self.removeItem(device)
    
    def getItem(self, index):
        return self.data[index-1]

class SimpleServerBrowser(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent = parent)
        self.setupUI()
        self.soap = SOAPClient();
        
    def setupUI(self):
        vlay = QVBoxLayout()
        self.servers = ServerListModel()
        self.serversCombo = combo = QComboBox()
        #combo.addItem('Wybierz serwer')
        combo.setModel(self.servers)
        vlay.addWidget(combo)
        
        self.tree = tree = QTreeWidget()
        vlay.addWidget(tree)
        self.setLayout(vlay)
        
        QWidget.connect(combo, SIGNAL('currentIndexChanged(int)'), self.serverChanged)
        QWidget.connect( self.tree, SIGNAL("itemDoubleClicked(QTreeWidgetItem*,int)"), self.itemDblClicked)
    
    def _queryServer(self, objectId):
        device = self.servers.getItem(self.serversCombo.currentIndex())
        service = device.findService("ContentDirectory")
        resp = self.soap.invokeActionByName(service, 'Browse', 
            {
                'ObjectID': str(objectId),
                'BrowseFlag': 'BrowseDirectChildren',
                'Filter': '',
                'StartingIndex': '0',
                'RequestedCount': '0',
                'SortCriteria': ''
            })
        xml = resp['Result']
        parser = DIDLParser()
        return parser.parse(xml)
            
    def serverChanged(self, index):
        r = self._queryServer(0)
        self.tree.clear()
        for item in r:
            treeItem = QTreeWidgetItem(None, [item.title])
            treeItem.object = item            
            self.tree.addTopLevelItem(treeItem)            
        
    def itemDblClicked(self, treeItem, column):
        item = treeItem.object
        if item.type == DIDLParser.TYPE_CONTAINER and treeItem.childCount() == 0:
            iid = item.attr['id']            
            r = self._queryServer(iid)
            for ch in r:
                newItem = QTreeWidgetItem(treeItem, [ch.title + ', ' +ch.attr['id']])
                newItem.object = ch
        elif item.type == DIDLParser.TYPE_ITEM:
            self.emit(SIGNAL("play"), item.res, item.didl)
        
        
    