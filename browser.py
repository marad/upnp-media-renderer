'''
Created on 08-05-2012

@author: morti
'''

import upnpy
from gui.SimpleServerBrowser import SimpleServerBrowser 

def callback(dev, state):
    print dev.friendlyName, ",", state

if __name__ == '__main__':
    
    upnpy.remoteDeviceManager.addDeviceCallback(callback)
    
    browser = SimpleServerBrowser()
    browser.show()
    
    upnpy.run()