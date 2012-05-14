'''
Created on 08-05-2012

@author: morti
'''

import upnpy
#from gui.browser import SimpleServerBrowser
from gui.player import Player 

#def callback(dev, state):
#    print dev.friendlyName, ",", state

if __name__ == '__main__':
    
    #upnpy.remoteDeviceManager.addDeviceCallback(callback)
    
    #window = SimpleServerBrowser()
    window = Player()
    window.show()
    
    upnpy.run()