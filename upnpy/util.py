'''
Created on 23-02-2012

@author: morti
'''

import re

class Entity(object):
    pass

class RegexUtil(object):
    
    tagNameMatcher = re.compile(r"^({[^}]*})?(.*)$")
    rootDeviceMatcher = re.compile(r"^upnp:rootdevice$")
    deviceTypeMatcher = re.compile(r"^(?:urn:[^:]+:device:)|(?:uuid:.+)")    
    serviceTypeMatcher = re.compile(r"^urn:[^:]+:service:")
    uuidMatcher = re.compile(r"^(?P<uuid>uuid:[^:]+)(?:::)?(?P<type>.*)$")
    baseURLMatcher = re.compile(r"^(?P<baseURL>[^:]+://[^:]+:[0-9]+).*$")
    
    maxAgeMatcher = re.compile(r"max-age=(?P<maxAge>[0-9]+)")
    
    @staticmethod
    def getUUID(string):
        return RegexUtil.uuidMatcher.match(string).group('uuid')
    
    @staticmethod
    def getBaseUrl(string):
        return RegexUtil.baseURLMatcher.match(string).group('baseUrl')
    
    @staticmethod
    def getMaxAge(string):
        return int(RegexUtil.maxAgeMatcher.search(string).group('maxAge'))
