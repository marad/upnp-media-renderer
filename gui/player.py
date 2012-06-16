# -*- coding: utf-8 -*-
'''
Created on 13-05-2012

@author: morti
'''
from PyQt4.QtGui import QWidget, QHBoxLayout, QMainWindow, QDockWidget
from PyQt4.QtCore import SIGNAL, Qt

from gui.browser import SimpleServerBrowser
#from gui.video import VideoPlayer
from gui import video
import upnpy

class Player(QMainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle("UPnP Media Renderer")
        self.setupUI()
        
    def setupUI(self):
        
        self.browser = browser = SimpleServerBrowser()
        self.player = player = video.Player() #VideoPlayer()        
        
        dock = QDockWidget(u'Przeglądarka serwerów', self)
        dock.setContentsMargins(0, 0, 0, 0)
        
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(browser)        
        
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)        
                
        #self.setCentralWidget(player.videoWidget())
        self.setCentralWidget(player.videoWidget)
        
        dock = QDockWidget(self)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        dock.setWidget(player.controlPanel)
        
        dock.setFloating(False)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
    
        QWidget.connect(self.browser, SIGNAL("play"), self.play)
        self.resize(800, 480)

    def itemSelected(self, url, didl):
        self.play(url)
        self.currentDIDL = didl
        
    def play(self, url = None, didl = None):
        if url:
            self.player.setCurrentSource(url, didl)
        self.player.play()

    
    def stop(self):
        self.player.stop()
    
    def pause(self):
        self.player.pause()
    
    def seek(self, target, unit):
        self.player.seek(target, unit)
    
    def setCurrentSource(self, url):
        self.player.setCurrentSource(url)
        
    def isPlaying(self):
        return self.player.isPlaying()
    
    def getPosition(self):
        return self.player.getPosition()
