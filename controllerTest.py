'''
Created on 24-02-2012

@author: morti
'''
#!/usr/bin/python


# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
from PyQt4.QtGui import QApplication, QWidget, QPushButton, QBoxLayout, QSizePolicy
app = QApplication(sys.argv)
import qt4reactor
qt4reactor.install(app)
from twisted.internet import reactor
######################################################
    
from upnpy.ssdp import SSDP
from upnpy.soap import SOAPClient
from gui.SimpleController import SimpleController

if __name__ == "__main__":
    
    widget = SimpleController()    
    widget.setVisible(True)
    
    reactor.run() #@UndefinedVariable
