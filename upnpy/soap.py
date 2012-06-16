'''
Created on 24-02-2012

@author: morti
'''
from consts import USER_AGENT
from time import strftime, gmtime

from twisted.internet.protocol import Protocol
import socket, re, traceback

class NoSuchActionError(ValueError):
    pass

class EmptyResponseException(Exception):
    pass

class InvalidResponseException(Exception):
    pass

class MissingOutputArgumentException(Exception):
    def __init__(self, argName):
        self.argName = argName

htmlCodes = (
    ('&', '&amp;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('"', '&quot;'),
    ("'", '&#39;'),
)

def encode(string):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def decode(string):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return string.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;','>').replace('&quot;', '"').replace('&#39;', "'")


ENVELOPE_TPL = '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
ENVELOPE_TPL+= '<s:Body>%s</s:Body></s:Envelope>'

ARG_TPL = "<%(name)s>%(value)s</%(name)s>"

REQ_TPL = ENVELOPE_TPL % '<u:%(actionName)s xmlns:u="%(urn)s">%(args)s</u:%(actionName)s>'
RESP_TPL = ENVELOPE_TPL % '<u:%(actionName)sResponse xmlns:u="%(urn)s">%(args)s</u:%(actionName)sResponse>'


REQ_HEADERS = 'POST %(path)s HTTP/1.0\r\n'
REQ_HEADERS+= 'HOST: %(host)s\r\n'    
REQ_HEADERS+= 'CONTENT-LENGTH: %(contentLen)s\r\n'
REQ_HEADERS+= 'CONTENT-TYPE: text/xml; charset="utf-8"\r\n'
REQ_HEADERS+= 'USER-AGENT: ' + USER_AGENT + '\r\n' 
REQ_HEADERS+= 'SOAPACTION: "%(action)s"\r\n\r\n'

RESP_HEADERS = 'HTTP/1.1 200 OK\r\n'
RESP_HEADERS+= 'CONTENT-TYPE: text/xml; charset=utf-8\r\n'
RESP_HEADERS+= 'DATE: %(date)s\r\n'        
RESP_HEADERS+= 'SERVER: ' + USER_AGENT + '\r\n' 
RESP_HEADERS+= 'CONTENT-LENGTH: %(contentLen)s\r\n'
RESP_HEADERS+= 'CONNECTION: close\r\n\r\n'


def soapSend(address, soapMessage):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(address)
        s.sendall(soapMessage)
        resp = ''
        while 1:
            data = s.recv(1024)            
            if not data: break
            resp += data
    except:
        traceback.print_exc()
    finally:
        s.close()
        
    return resp

class SOAPResponseParser(object):
    
    def __init__(self, action):
        self.action = action
        
    def parse(self, xml):
        
        ret = {}
        for arg  in self.action.argumentList.values():
            if arg.direction == arg.DIR_IN: continue
            
            match = re.search( '<[^:]*:?%(tag)s>([^<]*)</[^:]*:?%(tag)s>' % {'tag': arg.name}, xml)
            if not match:
                raise MissingOutputArgumentException(arg.name)
            ret[arg.name] = decode(match.group(1))
            
        return ret

class SOAPRequestParser(object):
    def parse(self, action, xml):
        ret = {}
        for arg in action.argumentList.values():
            if arg.direction == arg.DIR_OUT: continue
            
            match = re.search( '<[^:]*:?%(tag)s>([^<]*)</[^:]*:?%(tag)s>' % {'tag': arg.name}, xml)
            if not match:
                continue
            ret[arg.name] = decode(match.group(1))
            
        return ret
        
class SOAPSendRequest(Protocol):
    
    def __init__(self, soapRequest):
        self.soapRequest = soapRequest
    
    def connectionMade(self):
        self.transport.write(self.soapRequest)
        
    def dataReceived(self, data):
        print 'SOAP RESPONSE: ' + data
        
class SOAPClient(object):

    def _genRequest(self, service, action, inArgs=None):
        
        host = service.host + ':' + str(service.port)
        
        args = ''
        if inArgs != None:
            for k, v in inArgs.iteritems(): #zip(inArgs.keys(), inArgs.values()):
                args += ARG_TPL % {'name':str(k), 'value':encode(str(v))}
        
        actionId = service.serviceType +'#'+action.name
                
        xml = REQ_TPL % {'actionName': action.name,
                              'urn': service.serviceType,
                              'args': args}
        
        hdr = REQ_HEADERS % {'path': service.controlURL,
                              'host': host,
                              'contentLen': len(xml),
                              'action': actionId}
        return hdr + xml
    
#    def _genResponse(self, service, action, outArgs=None):
#        args = ''
#        if outArgs != None:
#            for k, v in outArgs.iteritems(): #zip(outArgs.keys(), outArgs.values()):
#                args += ARG_TPL % {'name':str(k), 'value':encode(str(v))}
#        
#        actionId = service.serviceId +'#'+action.name
#        
#        xml = RESP_TPL % {'actionName': action.name,
#                              'urn': actionId,
#                              'args': args}
#        
#        hdr = RESP_HEADERS % {'path': service.controlURL,
#                                   #'date': strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime()),
#                                   'date' : 'Tue, 15 May 2012 14:25:28 GMT',
#                                   'contentLen': len(xml),
#                                   'action': actionId}
#        
#        return hdr + xml
    
    def invokeAction(self, service, action, args):        
        req = self._genRequest(service, action, args)

        resp = soapSend((service.host, service.port), req)
    
        parser = SOAPResponseParser(action)
        try:    
            return parser.parse(resp[resp.find('<'):])
        except:
            raise InvalidResponseException()
    
    def invokeActionByName(self, service, actionName, args):
        action = service.actions[actionName]
        
        if not action:
            raise NoSuchActionError()
        
        return self.invokeAction(service, action, args)
    
class SOAPResponse(object):
    
    def generate(self, service, actionName, outArgs=None):
        
        action = service.actions[actionName]
        
        args = ''
        if outArgs != None:
            for k, v in outArgs.iteritems(): #zip(outArgs.keys(), outArgs.values()):
                args += ARG_TPL % {'name':str(k), 'value':encode(str(v))}
        
        actionId = service.serviceId +'#'+action.name
        
        xml = RESP_TPL % {'actionName': action.name,
                           'urn': service.serviceType,
                           'args': args}
        
        hdr = RESP_HEADERS % {'date': strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime()),
                              'contentLen': len(xml)}
        
        return xml
