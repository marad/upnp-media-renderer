'''
Created on 08-05-2012

@author: morti
'''

import upnpy
from gui.player import Player 

if __name__ == '__main__':
    
    window = Player()
    window.show()
    
    upnpy.run()