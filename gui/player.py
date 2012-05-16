# -*- coding: utf-8 -*-
'''
Created on 13-05-2012

@author: morti
'''
from PyQt4.QtGui import QWidget, QHBoxLayout, QMainWindow, QDockWidget
from PyQt4.QtCore import SIGNAL, Qt

from gui.browser import SimpleServerBrowser
from gui.video import VideoPlayer

class Player(QMainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle("UPnP Media Renderer")
        self.setupUI()
        
    def setupUI(self):
        
        self.browser = browser = SimpleServerBrowser()
        self.player = player = VideoPlayer()        
        
        dock = QDockWidget(u'Przeglądarka serwerów', self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(browser)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        
        self.setCentralWidget(player.videoWidget())
    
        QWidget.connect(self.browser, SIGNAL("play"), self.player.showURL)
        self.resize(800, 480)
    
    def play(self, url):
        if self.player.isPaused():
            self.player.pause()
        else:
            self.player.showURL(url)
    
    def stop(self):
        self.player.stop()
    
    def pause(self):
        self.player.pause()
    
    def seek(self, target, unit):
        #self.player.seek()
        pass