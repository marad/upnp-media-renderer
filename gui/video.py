'''
Created on 13-05-2012

@author: morti
'''
from PyQt4.phonon import Phonon

class VideoPlayer(Phonon.VideoPlayer):
    def __init__(self):
        Phonon.VideoPlayer.__init__(self, Phonon.VideoCategory)
    
    def showURL(self, url):
        source = Phonon.MediaSource(url)
        self.play(source)
        