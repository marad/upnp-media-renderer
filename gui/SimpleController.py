# -*- coding: utf-8 -*-
'''
Created on 24-02-2012

@author: morti
'''

from upnpy.ssdp import SSDP
from upnpy.soap import SOAP

from PyQt4.QtGui import QWidget, QBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QTextEdit
from PyQt4.QtCore import SIGNAL

class ActionWindow(QWidget):
    def __init__(self, service, action):
        QWidget.__init__(self)
        self.setupUI()
        self.soap = SOAP()
        self.service = service
        self.action = action
        
    def setupUI(self):
        self.setWindowTitle('Service view')
        
        vlay = QBoxLayout(QBoxLayout.TopToBottom)
        
        for arg in self.action.argumentList.values():
            hlay = QBoxLayout(QBoxLayout.LeftToRight)
            hlay.addWidget(QLabel(arg.name))
            hlay.addWidget(QTextEdit())
            vlay.addLayout(hlay)
        
        self.setLayout(vlay)
        
        

class SimpleController(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUI()
        self.knownDevices = []
        self.ssdp = SSDP()
        self.ssdp.addHandler(self.deviceFound)
        self.ssdp.listen()
        self.ssdp.search(target='upnp:rootdevice')
    
    def setupUI(self):
        
        self.setWindowTitle("Simple UPnP Controller")
        self.resize(600, 400)
        
        self.tree = QTreeWidget()
        self.content = QWidget()       
        
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabel('Urzadzenia')
        QWidget.connect( self.tree, SIGNAL("itemDoubleClicked()"), self.actionActivated)      
        
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tree, 2)
        #layout.addWidget(self.content, 3)
        
        self.setLayout(layout)
    
    def deviceFound(self, headers, device):        
        self.addDevice(device)
    
    def addDevice(self, device, parentItem = None):
        print device
        if not (device.UDN in self.knownDevices):
            
            devItem = QTreeWidgetItem(parentItem, [device.friendlyName])
            devItem.device = device
            
            for subDev in device.devices.values():
                self.addDevice(subDev, devItem)
                
            for srv in device.services.values():
                srvItem = QTreeWidgetItem(devItem, [srv.serviceId])
                srvItem.service = srv
                for action in srv.actions.values():
                    actItem = QTreeWidgetItem(srvItem, [action.name])
                    actItem.action = action
                    actItem.service = srv
                    
                    srvItem.addChild(actItem)                
                devItem.addChild(srvItem)
            
            if parentItem == None:
                self.tree.addTopLevelItem(devItem)
            else:
                parentItem.addChild(devItem)
            
            self.knownDevices.append(device.UDN)
    
    def actionActivated(self, item, column):
        print item, column