'''
Created on 24-02-2012

@author: morti
'''
#!/usr/bin/python


# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
#import sys
#from PyQt4.QtGui import QApplication, QWidget, QPushButton, QBoxLayout, QSizePolicy
#app = QApplication(sys.argv)
#import qt4reactor
#qt4reactor.install(app)
#from twisted.internet import reactor
######################################################

import upnpy

from gui.SimpleController import SimpleController

if __name__ == "__main__":

    widget = SimpleController()
    widget.setVisible(True)

    upnpy.run()
    #reactor.run()         #@UndefinedVariable
    #reactor.getThreadPool().stop()        #@UndefinedVariable
