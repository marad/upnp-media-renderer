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
        
        self.deviceType = None
        self.friendlyName = None
        self.manufacturer = None
        self.manufacturerURL = None
        self.modelDescription = None
        self.modelNumber = None
        self.modelName = None
        self.modelURL = None
        self.serialNumber = None
        self.UDN = None
        self.presentationURL = None
        self.baseURL = None
        self.rootDescURL = None
        #self.location = deviceDesc.location

    
        
########################################################################
# Represents UPnP device Service
class Service(object):    
    #@property
    #def SCPDURL(self):
    #    def fget(self):
    #        return "%s/%s" % (self.baseURL, self._SCPDURL)
    
    def __init__(self):
        self.baseURL = None
        self.device = None
        self.serviceType = None
        self.serviceId = None
        self._controlURL = None
        self._eventSubURL = None
        self._SCPDURL = None
        #self.actions, self.stateVariables = _parseSCPD(self.device.location.rstrip('/') + '/' + self.SCPDURL.lstrip('/'))
        self.actions = {}
        self.stateVariables = {}
        
    
    def invokeMethod(self, name, kwargs):
        method = getattr(self, name)
        method(*kwargs)
    
    def addStateVariable(self, stVar=None, descDict=None):

        if stVar != None:
            self.stateVariables[stVar.name] = stVar
        elif descDict != None:
            stVar = StateVariable(**descDict)
            self.addStateVariable(stVar)
        
    def addAction(self, action):
        self.actions[action.name] = action
        
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
        try:
            return re.search('^[^:]+://([^/:]*)', self.baseURL).group(1)
        except:
            return ""
    
    @property
    def port(self):
        try:
            return int(re.search('^[^:]+://[^/:]*:([^/]*)', self.baseURL).group(1))
        except:
            return 0
    
    @property
    def friendlyName(self):
        try:
            match = re.search('urn:upnp-org:serviceId:([^:]*):(.*)', self.serviceId)
            return "%s (v%s)" % (match.group(1), match.group(2)) 
        except:
            return self.serviceId
    
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
    
    def __init__(self, 
                 name = None,
                 dataType = None,
                 defaultValue = None,
                 allowedValueList = [],
                 allowedValueRangeMin = None,
                 allowedValueRangeMax = None,
                 allowedValueRangeStep = None,
                 sendEvents = None,
                 multicast = None):
        self.name = name
        self.dataType = dataType
        self.defaultValue = defaultValue
        self.allowedValueList = allowedValueList
        self.allowedValueRange = Entity()
        self.allowedValueRange.min = allowedValueRangeMin
        self.allowedValueRange.max = allowedValueRangeMax
        self.allowedValueRange.step = allowedValueRangeStep
        self.sendEvents = sendEvents
        self.multicast = multicast

########################################################################
# Holds service action argument information
class ActionArgument(object):
    DIR_IN = "in"
    DIR_OUT = "out"
    def __init__(self, 
                 name=None,
                 direction=None,
                 retval=None,
                 relatedStateVariable=None):
        self.name = name
        self.direction = direction
        self.retval =  retval
        self.relatedStateVariable = relatedStateVariable
        self.relatedStateVariableRef = None

########################################################################
# Represents service action
class Action(object):
    def __init__(self,
                 name=None,
                 argumentList={}):
        self.name = name
        self.argumentList = argumentList
        
    def addArgument(self, arg):
        self.argumentList[arg.name] = arg
    
    @property
    def args(self):
        return self.argumentList.values()
    
    @property
    def argNames(self):
        return self.argumentList.keys() 