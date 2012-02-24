'''
Created on 24-02-2012

@author: morti
'''
from upnpy import USER_AGENT
from time import strftime, gmtime

from twisted.internet.protocol import Protocol
import socket, re

class NoSuchActionError(ValueError):
    pass

class EmptyResponseException(Exception):
    pass

class SOAPResponseParser(object):
    
    def __init__(self, action):
        self.action = action
        
    def parse(self, xml):
        
        #print "XML:",xml
        
        ret = {}
        for arg  in self.action.argumentList.values():
            if arg.direction == arg.DIR_IN: continue
            
            match = re.search('<%(tag)s>([^<]*)</%(tag)s>' % {'tag': arg.name}, xml)
            if not match:
                raise EmptyResponseException()
            ret[arg.name] = match.group(1)
            
        return ret
    
class SOAPSendRequest(Protocol):
    
    def __init__(self, soapRequest):
        self.soapRequest = soapRequest
    
    def connectionMade(self):
        self.transport.write(self.soapRequest)
        
    def dataReceived(self, data):
        print 'SOAP RESPONSE: ' + data
        
class SOAP(object):
    ENVELOPE_TPL = '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
    ENVELOPE_TPL+= '<s:Body>%s</s:Body></s:Envelope>'
    
    ARG_TPL = "<%(name)s>%(value)s</%(name)s>\r\n"
    
    REQ_TPL = ENVELOPE_TPL % '<u:%(actionName)s xmlns:u="%(urn)s">%(args)s</u:%(actionName)s>'
    RESP_TPL = ENVELOPE_TPL % '<u:%(actionName)sResponse xmlns:u="%(urn)s">%(args)s</u:%(actionName)sResponse>'

    
    REQ_HEADERS = 'POST %(path)s HTTP/1.0\r\n'
    REQ_HEADERS+= 'HOST: %(host)s\r\n'    
    REQ_HEADERS+= 'CONTENT-LENGTH: %(contentLen)s\r\n'
    REQ_HEADERS+= 'CONTENT-TYPE: text/xml; charset="utf-8"\r\n'
    REQ_HEADERS+= 'USER-AGENT: ' + USER_AGENT + '\r\n' 
    REQ_HEADERS+= 'SOAPACTION: "%(action)s"\r\n\r\n'
    
    RESP_HEADERS = 'POST %(path)s HTTP/1.0\r\n'
    RESP_HEADERS+= 'DATE: %(date)s\r\n'        
    RESP_HEADERS+= 'SERVER: ' + USER_AGENT + '\r\n' 
    RESP_HEADERS+= 'CONTENT-LENGTH: %(contentLen)s\r\n'        

    def _genRequest(self, service, action, inArgs=None):
        
        host = service.host + ':' + str(service.port)
        
        args = ''
        if inArgs != None:
            for k, v in zip(inArgs.keys(), inArgs.values()):
                args += self.ARG_TPL % {'name':k, 'value':v}
        
        actionId = service.serviceType +'#'+action.name
                
        
        xml = self.REQ_TPL % {'actionName': action.name,
                              'urn': service.serviceType,
                              'args': args}
        
        hdr = self.REQ_HEADERS % {'path': service.controlURL,
                              'host': host,
                              'contentLen': len(xml),
                              'action': actionId}
        return hdr + xml
    
    def _genResponse(self, service, action, outArgs=None):
        args = ''
        if outArgs != None:
            for k, v in zip(outArgs.keys(), outArgs.values()):
                args += self.ARG_TPL % {'name':k, 'value':v}
        
        actionId = service.serviceId +'#'+action.name
        
        xml = self.RESP_TPL % {'actionName': action.name,
                              'urn': actionId,
                              'args': args}
        
        hdr = self.RESP_HEADERS % {'path': service.controlURL,
                                   'date': strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime()),
                                   'contentLen': len(xml),
                                   'action': actionId}
        
        return hdr + xml
    
    def invokeAction(self, service, action, args):        
        req = self._genRequest(service, action, args)
        
        #print 'Sending SOAP:', req
        #print service.host, service.port
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((service.host, service.port))
        s.sendall(req)
        resp = ''
        while 1:
            data = s.recv(1024)            
            if not data: break
            resp += data
        s.close()
    
        #print resp
        parser = SOAPResponseParser(action)    
        return parser.parse(resp[resp.find('<'):])
    
    def invokeActionByName(self, service, actionName, args):
        action = service.actions[actionName]
        
        if not action:
            raise NoSuchActionError()
        
        return self.invokeAction(service, action, args)