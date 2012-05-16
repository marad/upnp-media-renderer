'''
Created on 23-02-2012

@author: morti
'''

import re, socket

class Entity(object):
    pass

class RegexUtil(object):
    
    tagNameMatcher = re.compile(r"^({[^}]*})?(.*)$")
    rootDeviceMatcher = re.compile(r"^upnp:rootdevice$")
    deviceTypeMatcher = re.compile(r"^(?:urn:[^:]+:device:)|(?:uuid:.+)")    
    serviceTypeMatcher = re.compile(r"^urn:[^:]+:service:")
    uuidMatcher = re.compile(r"^(?P<uuid>uuid:[^:]+)(?::)?(?P<type>.*)$")
    baseURLMatcher = re.compile(r"^(?P<baseURL>[^:]+://[^:]+:[0-9]+).*$")
    serverNameMatcher = re.compile(r"^[^:]+://(?P<address>[^:/]+):?(?P<port>[0-9]+)?/")
    
    maxAgeMatcher = re.compile(r"max-age\s*=\s*(?P<maxAge>[0-9]+)")
    
    @staticmethod
    def isRootDevice(type):
        return RegexUtil.rootDeviceMatcher.match(type) != None 
    
    @staticmethod
    def getUUID(string):
        return RegexUtil.uuidMatcher.match(string).group('uuid')
    
    @staticmethod
    def getBaseUrl(string):
        return RegexUtil.baseURLMatcher.match(string).group('baseUrl')
    
    @staticmethod
    def getMaxAge(string):
        return int(RegexUtil.maxAgeMatcher.search(string).group('maxAge'))
    
    @staticmethod
    def getServerAndPortFromURL(string):
        match = RegexUtil.serverNameMatcher.match(string)
        return ( match.group('address'), match.group('port') )

def interfaces():
    return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]

def localInterface():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:        
        s.connect(('1.1.1.1', 0))
        return s.getsockname()[0]
    except: pass
    finally:
        s.close()
