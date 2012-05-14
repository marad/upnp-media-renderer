'''
Created on 13-05-2012

@author: morti
'''
from PyQt4.QtGui import QWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QTextEdit
from PyQt4.QtGui import QPushButton, QGroupBox, QLineEdit, QMessageBox, QComboBox
from PyQt4.QtCore import SIGNAL, QAbstractListModel, Qt, QModelIndex, QVariant

from gui.browser import SimpleServerBrowser
from gui.video import VideoPlayer

class Player(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle("UPnP Media Renderer")
        self.setupUI()
        
    def setupUI(self):
        hlay = QHBoxLayout()
        
        self.browser = browser = SimpleServerBrowser()
        self.player = player = VideoPlayer()        
        
        hlay.addWidget(browser)
        hlay.addWidget(player.videoWidget())
    
        self.setLayout(hlay)
    
        QWidget.connect(self.browser, SIGNAL("play"), self.player.showURL)