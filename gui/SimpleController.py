# -*- coding: utf-8 -*-
'''
Created on 24-02-2012

@author: morti
'''

from upnpy.ssdp import SSDP
from upnpy.soap import SOAPClient

from PyQt4.QtGui import QWidget, QBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QTextEdit
from PyQt4.QtGui import QPushButton, QGroupBox, QLineEdit, QMessageBox
from PyQt4.QtCore import SIGNAL

class ActionWindow(QWidget):
    def __init__(self, service, action):
        QWidget.__init__(self, parent=None)
        self.service = service
        self.action = action
        self.args = {}
        self.outs = {}
        
        self.setupUI()
        self.soap = SOAPClient()
        
    def setupUI(self):
        self.setWindowTitle('Service view')
        
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        
        inGroup = QGroupBox('Input Arguments')
        vlay = QBoxLayout(QBoxLayout.TopToBottom)
        
        for arg in self.action.argumentList.values():
            if arg.direction == arg.DIR_OUT: continue
            #print 'Argument: ', arg.name
            
            edit = QLineEdit()
            QWidget.connect(edit, SIGNAL('textChanged(QString)'), lambda x: self.textChanged(arg.name, edit))
            
            hlay = QBoxLayout(QBoxLayout.LeftToRight)
            hlay.addWidget(QLabel(arg.name))
            hlay.addWidget(edit)
            vlay.addLayout(hlay)
        
        if vlay.count() > 0:
            inGroup.setLayout(vlay)
            layout.addWidget(inGroup)
        
        outGroup = QGroupBox('Output Arguments')
        vlay = QBoxLayout(QBoxLayout.TopToBottom)
        for arg in self.action.argumentList.values():            
            if arg.direction == arg.DIR_IN: continue
            #print 'Argument: ', arg.name
            
            edit = QLineEdit()
            self.outs[arg.name] = edit
            
            hlay = QBoxLayout(QBoxLayout.LeftToRight)
            hlay.addWidget(QLabel(arg.name))
            hlay.addWidget(edit)
            vlay.addLayout(hlay)
           
        if vlay.count() > 0: 
            outGroup.setLayout(vlay)
            layout.addWidget(outGroup)
                 
        button = QPushButton('Invoke')
        QWidget.connect(button, SIGNAL('clicked()'), self.sendSoap)
        
        layout.addWidget(button)
        
        self.setLayout(layout)
        self.adjustSize()
        
    def textChanged(self, argName, edit):
        self.args[argName] = edit.text()
        
    def sendSoap(self):        
        out = self.soap.invokeAction(self.service, self.action, self.args)
        
        if out == None:
            QMessageBox.warning(self, 'Oops!', 'There was a problem with communication!')
        else:
            for name, value in zip(out.keys(), out.values()):
                edit = self.outs[name]
                edit.setText(value)

class SimpleController(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUI()
        self.knownDevices = []
        self.ssdp = SSDP()
        self.ssdp.addHandler(self.deviceFound)
        self.ssdp.listen()
        self.ssdp.search(target='upnp:rootdevice', mx=1)
        self.act = None
    
    def setupUI(self):
        
        self.setWindowTitle("Simple UPnP Controller")
        self.resize(600, 400)
        
        self.tree = QTreeWidget()
        self.content = QWidget()       
        
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabel('Urzadzenia')
        QWidget.connect( self.tree, SIGNAL("itemDoubleClicked(QTreeWidgetItem*,int)"), self.actionActivated)      
        
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tree, 2)
        #layout.addWidget(self.content, 3)
        
        self.setLayout(layout)
    
    def deviceFound(self, headers, device):        
        self.addDevice(device)
    
    def addDevice(self, device, parentItem = None):        
        if not (device.UDN in self.knownDevices):
            
            devItem = QTreeWidgetItem(parentItem, [device.friendlyName])
            devItem.device = device
            
            for subDev in device.devices.values():
                self.addDevice(subDev, devItem)
                
            for srv in device.services.values():
                srvItem = QTreeWidgetItem(devItem, [srv.friendlyName])
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
        if 'action' in vars(item).keys():
            #print 'Opening window for action', item.action.name
            self.act = ActionWindow(item.service, item.action)
            self.act.resize(300, 200)
            self.act.setVisible(True)