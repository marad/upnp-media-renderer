'''
Created on 08-05-2012

@author: morti
'''

# THIS BLOCK NEEDS TO BE EXECUTED BEFORE ANYTHING ELSE
import sys
from PyQt4.QtGui import QApplication, QWidget, QPushButton, QBoxLayout, QSizePolicy
app = QApplication(sys.argv)
import qt4reactor
qt4reactor.install(app)
from twisted.internet import reactor
######################################################

from gui.SimpleServerBrowser import SimpleServerBrowser

if __name__ == '__main__':
    
    SimpleServerBrowser().setVisible(True)
    
    reactor.run()  # @UndefinedVariable
    reactor.getThreadPool().stop()  # @UndefinedVariable