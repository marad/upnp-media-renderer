'''
Created on 24-02-2012

@author: morti
'''

from twisted.internet.protocol import Protocol, ClientFactory

class Controller(Protocol):
    def dataReceived(self, data):
        print data

class ControllerFactory(ClientFactory):
    protocol = Controller