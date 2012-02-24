'''
Created on 19-02-2012

@author: morti
'''

import re
from upnpy.util import Entity
        
########################################################################
# Holds device icon information
class Icon(object):
    def __init__(self, device=None, mimetype=None, width=None, height=None, depth=None, url=None):
        self.device = device
        self.mimetype = mimetype
        self.width = width
        self.height = height
        self.depth = depth
        self.url = url
        
########################################################################
# Represents UPnP device
class Device(object):
    #def __init__(self, type=None, friendlyName=None, 
    #             manufacturer=None, manufacturerURL=None,
    #             modelDescription=None, modelNumber=None, modelName=None, modelURL=None,
    #             serialNumber=None, udn=None, presentationURL=None, location=None):
#    def __init__(self, deviceDesc=None, rootXml=None):
    def __init__(self):
        self.devices = {}
        self.services = {} # service id => service
        self.icons = [] # icon list
        
        self.deviceType = ""
        self.friendlyName = ""
        self.manufacturer = ""
        self.manufacturerURL = ""
        self.modelDescription = ""
        self.modelNumber = ""
        self.modelName = ""
        self.modelURL = ""
        self.serialNumber = ""
        self.UDN = ""
        self.presentationURL = ""
        self.baseURL = ""
        self.rootDescURL = ""
        #self.location = deviceDesc.location

    
        
########################################################################
# Represents UPnP device Service
class Service(object):    
    #@property
    #def SCPDURL(self):
    #    def fget(self):
    #        return "%s/%s" % (self.baseURL, self._SCPDURL)
    
    def __init__(self):
        self.baseURL = ""
        self.device = ""
        self.serviceType = ""
        self.serviceId = ""
        self._controlURL = ""
        self._eventSubURL = ""
        self._SCPDURL = ""
        #self.actions, self.stateVariables = _parseSCPD(self.device.location.rstrip('/') + '/' + self.SCPDURL.lstrip('/'))
        self.actions = {}
        self.stateVariables = {}
        
    def _findBaseUrl(self, val):
        match = re.search('^[^:]+://[^/]*', val)
        if match == None:
            return self.baseURL
        else:
            return match.group(0)
     
    @property
    def SCPDURL(self):
        return self._SCPDURL 
    
    @SCPDURL.setter
    def SCPDURL(self, val):
        base = self._findBaseUrl(val)
        self.SCPDPath = val
        self._SCPDURL = base.rstrip('/') + '/' + val.lstrip('/')
        
    @property
    def host(self):
        return re.search('^[^:]+://([^/:]*)', self.baseURL).group(1)
    
    @property
    def port(self):
        return int(re.search('^[^:]+://[^/:]*:([^/]*)', self.baseURL).group(1))
    
#    @property
#    def controlURL(self):
#        return self._controlURL
#    
#    @controlURL.setter
#    def controlURL(self, val):
#        base = self._findBaseUrl(val)
#        self.controlURLPath = val
#        self._controlURL = base.rstrip('/') + '/' + val.lstrip('/')
        
#    @property
#    def eventSubURL(self):
#        return self._eventSubURL
#    
#    @eventSubURL.setter
#    def eventSubURL(self, val):
#        base = self._findBaseUrl(val)
#        self.eventSubURLPath = val
#        self._eventSubURL = base.rstrip('/') + '/' + val.lstrip('/')
    
########################################################################
# Holds service state variable information
class StateVariable(object):
    TYPE_UI1        = "ui1"
    TYPE_UI2        = "ui2"
    TYPE_UI4        = "ui4"
    TYPE_I1         = "i1"
    TYPE_I2         = "i2"
    TYPE_I4         = "i4"
    TYPE_INT        = "int"
    TYPE_R4         = "r4"
    TYPE_R8         = "r8"
    TYPE_NUMBER     = "number"
    TYPE_FIXED_14_4 = "fixed.14.4"
    TYPE_FLOAT      = "float"
    TYPE_CHAR       = "char"
    TYPE_STRING     = "string"
    TYPE_DATE       = "date"
    TYPE_DATETIME   = "dateTime"
    TYPE_DATETIME_TZ = "dateTime.tz"
    TYPE_TIME       = "time"
    TYPE_TIME_TZ    = "time.tz"
    TYPE_BOOLEAN    = "boolean"
    TYPE_BIN_BASE64 = "bin.base64"
    TYPE_BIN_HEX    = "bin.hex"
    TYPE_URI        = "uri"
    TYPE_UUID       = "uuid"
    
    def __init__(self):
        self.name = None
        self.dataType = None
        self.defaultValue = None
        self.allowedValueList = []
        self.allowedValueRange = Entity()
        self.allowedValueRange.min = None
        self.allowedValueRange.max = None
        self.allowedValueRange.step = None
        self.sendEvents = None
        self.multicast = None

########################################################################
# Holds service action argument information
class ActionArgument(object):
    DIR_IN = "in"
    DIR_OUT = "out"
    def __init__(self):
        self.name = None
        self.direction = None
        self.retval =  None
        self.relatedStateVariable = None

########################################################################
# Represents service action
class Action(object):
    def __init__(self):
        self.name = None
        self.argumentList = {}
        
    