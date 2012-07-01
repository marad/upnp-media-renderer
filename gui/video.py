'''
Created on 13-05-2012

@author: morti
'''
import re
from PyQt4.phonon import Phonon
from PyQt4.QtCore import QUrl, SIGNAL
from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QIcon
from upnpy.util import convertFromBoolean

#class VideoPlayer(Phonon.VideoPlayer):
#    def __init__(self):
#        Phonon.VideoPlayer.__init__(self, Phonon.VideoCategory)
    
#    def showURL(self, url):
#        source = Phonon.MediaSource(url)
#        self.play(source)


def milToTime(mils):
    sec = mils / 1000
        
    hour = sec / 3600
    sec = sec % 3600
    
    min = sec / 60
    sec = sec % 60
    return (hour, min, sec)

class MediaSourceInfo(object):
    def __init__(self, urlString, didl):
        url = QUrl(urlString)
        self.source = Phonon.MediaSource(url)
        self.urlString = urlString
        self.didl = didl


class Player(QWidget):
    TIME_PATTERN = "(?P<hour>[0-9]?[0-9]):(?P<min>[0-9]?[0-9]):(?P<sec>[0-9]?[0-9])"
    
    def __init__(self, parent = None):
        QWidget.__init__(self, parent = parent)
        self.currentSource = None
        
        self.currentDIDL = None
        self.nextSource = None
        self.prevSource = None
        
        self.setupUI()
    
    def setupUI(self):
        self.mediaObject = Phonon.MediaObject(self)
        self.videoWidget = Phonon.VideoWidget(self)
        self.audioOutput = Phonon.AudioOutput(self)
        
        Phonon.createPath(self.mediaObject, self.videoWidget)
        Phonon.createPath(self.mediaObject, self.audioOutput)
        
        self.controlPanel = QWidget(self)
        
        self.previousButton = QPushButton(QIcon("icons/previous.png"), "")
        self.playButton = QPushButton(QIcon("icons/play.png"), "")
        self.pauseButton = QPushButton(QIcon("icons/pause.png"), "")
        self.stopButton = QPushButton(QIcon("icons/stop.png"), "")
        self.nextButton = QPushButton(QIcon("icons/next.png"), "")
                
        vlay = QVBoxLayout()        
        controlLayout = QHBoxLayout()
        
        controlLayout.addStretch()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.pauseButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.addStretch()
        
        controlLayout.setContentsMargins(0, 0, 0, 0)
        
        seeklay = QVBoxLayout()
        seeklay.setContentsMargins(0, 0, 0, 0)
        
        self.seekSlider = Phonon.SeekSlider(self)
        self.seekSlider.setMediaObject(self.mediaObject)
        
        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setAudioOutput(self.audioOutput)
        
        controlLayout.addWidget(self.volumeSlider)
        
        seeklay.addWidget(self.seekSlider)
        seeklay.addLayout(controlLayout)
        
        self.controlPanel.setLayout(seeklay)    
         
        
        vlay.addWidget(self.videoWidget)
        vlay.addWidget(self.controlPanel)
        
        self.setLayout(vlay)
        
        QWidget.connect(self.playButton, SIGNAL("clicked()"), self.play)
        QWidget.connect(self.pauseButton, SIGNAL("clicked()"), self.pause)
        QWidget.connect(self.stopButton, SIGNAL("clicked()"), self.stop)      
        
    def setNextSource(self, urlString):
        self.nextSource = MediaSourceInfo(urlString, None)
            
    def setCurrentSource(self, urlString, didl = None):
        
        if self.prevSource:
            print "Stare zrodlo:", self.prevSource.urlString
        print "Nowe zrodlo:", urlString
            
        def changeSource(newSource):
            self.prevSource = self.currentSource
            self.currentSource = newSource
            self.mediaObject.setCurrentSource(newSource.source)
        
        if self.currentSource != None and self.currentSource.urlString == urlString:
            print "Zrodlo aktualne, nie zmieniam"
            pass 
        elif self.nextSource != None and self.nextSource.urlString == urlString:
            print "Wybieram nastepne zrodlo"
            changeSource(self.nextSource)
            self.nextSource = None
        elif self.prevSource != None and self.prevSource.urlString == urlString:
            print "Wybieram poprzednie zrodlo"
            self.nextSource = self.currentSource
            changeSource(self.prevSource)
            self.prevSource = None
        else:
            print "Wybieram nowe zrodlo..."
            self.nextSource = None            
            changeSource(MediaSourceInfo(urlString, didl))
            self.currentDIDL = didl
        
    def enqueue(self, url):
        self.mediaObject.enqueue(url)
        
    def play(self):
        self.mediaObject.play()
    
    def stop(self):
        self.mediaObject.stop()
        
    def prev(self):
        urlString = self.prevSource.urlString
        didl = self.prevSource.didl
        self.setCurrentSource(urlString, didl)
        
    def next(self):
        urlString = self.nextSource.urlString
        didl = self.nextSource.didl
        self.setCurrentSource(urlString, didl)
    
    def seek(self, pos, unit):
        mils = 0
        if unit == "REL_POS":
            mils = self.mediaObject.currentTime()
            
        result = re.search(self.TIME_PATTERN, pos)
        if result:
            hr = int( result.group("hour") )
            min = int( result.group("min") ) 
            sec = int( result.group("sec") )
            mils += 1000 * (sec + 60*min + 3600*hr)  
            self.mediaObject.seek(mils)
        else:
            print "Couldnt parse", pos
        
    def pause(self):
        self.mediaObject.pause()
        
    def isPlaying(self):
        state = self.mediaObject.state()
        return state == Phonon.BufferingState or state == Phonon.PlayingState
    
    def getPosition(self):
        return "%02d:%02d:%02d" % milToTime(self.mediaObject.currentTime())
    
    def getTotalTime(self):
        return "%02d:%02d:%02d" % milToTime(self.mediaObject.totalTime())
    
    def getVolume(self):
        return self.audioOutput.volume() * 100
    
    def setVolume(self, level):
        self.audioOutput.setVolume( float(level) / 100.0)
    
    def getMute(self):
        if self.audioOutput.isMuted():
            return 1
        else:
            return 0
    
    def setMute(self, mute):
        if convertFromBoolean(mute):
            self.audioOutput.setMuted(True)
        else:
            self.audioOutput.setMuted(False)
        
        