'''
Created on 08-05-2012

@author: morti
'''

import upnpy
from upnpy.soap import SOAPClient
from upnpy.xmlutil import DIDLParser
from gui.video import VideoPlayer

from PyQt4.QtGui import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QTextEdit
from PyQt4.QtGui import QPushButton, QGroupBox, QLineEdit, QMessageBox, QComboBox
from PyQt4.QtCore import SIGNAL, QAbstractListModel, Qt, QModelIndex, QVariant


class ServerListModel(QAbstractListModel):
    def __init__(self):
        QAbstractListModel.__init__(self)
        self.data = []
    
    def data(self, index, role):        
        if index.row() == 0:
            return 'Wybierz serwer...'
        else:
            return self.data[index.row()-1].friendlyName
        #if index.row() < len(self.data):
        #    return self.data[index.row()]
        #else:
        #    return None
    
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

class SimpleServerBrowser(QWidget):
    '''
    classdocs
    '''

    def __init__(self, parent = None):
        '''
        Constructor
        '''
        QWidget.__init__(self, parent = parent)
        
        self.setupUI()
        
        self.soap = SOAPClient();
        filter = 'MediaServer'
        upnpy.remoteDeviceManager.addDeviceCallback(self.deviceStatus)
        
    def setupUI(self):
        
        self.video = VideoPlayer()
        self.video.show()
        
        vlay = QVBoxLayout()
        
        self.serversCombo = combo = QComboBox()
        combo.addItem('Wybierz serwer')
        self.servers = ServerListModel()  
        combo.setModel(self.servers)
        vlay.addWidget(combo)
        
        self.tree = tree = QTreeWidget()
        
        
        vlay.addWidget(tree)
        self.setLayout(vlay)
        
        QWidget.connect(combo, SIGNAL('currentIndexChanged(int)'), self.serverChanged)
        QWidget.connect( self.tree, SIGNAL("itemDoubleClicked(QTreeWidgetItem*,int)"), self.itemDblClicked)
    
    def deviceStatus(self, device, status):        
        #self.serversCombo.addItem(device.friendlyName)
        if status == "NEW":
            self.servers.addItem(device)
            
    def _queryServer(self, objectId):
        device = self.servers.data[self.serversCombo.currentIndex()-1]
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
        for item in r:
            treeItem = QTreeWidgetItem(None, [item.title + '(' +item.attr['id']+ ')'])
            treeItem.object = item            
            self.tree.addTopLevelItem(treeItem)            
        
    def itemDblClicked(self, treeItem, column):
        item = treeItem.object
        
        print item.attr
        print dir(item)
        if item.type == DIDLParser.TYPE_CONTAINER:
            iid = item.attr['id']            
            print iid
            r = self._queryServer(iid)
            for ch in r:
                newItem = QTreeWidgetItem(treeItem, [ch.title + '(' + ch.attr['id'] + ')'])
                newItem.object = ch
        elif item.type == DIDLParser.TYPE_ITEM:
            print 'play:', item.res
            #self.video = VideoPlayer()
            #self.video.show()
            
            self.video.stop()
            self.video.showURL(item.res)
            
            #self.wideo = 
        
        
    