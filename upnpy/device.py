'''
Created on 19-02-2012

@author: morti
'''

import re
from lxml import etree
from upnpy.util import Entity

def _createNodesFromAttrs(obj, attrList, parent):
    #nodes = []
    for name in attrList:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value == None:
                continue
            node = etree.Element(name)
            node.text = str(value)
            parent.append(node)
        #nodes.append(node)
        
    #return nodes
        
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
    
    def toXML(self):
        icon = etree.Element('icon')
        _createNodesFromAttrs(self, ['mimetype', 
                                     'width', 'height',
                                     'depth', 'url'], 
                              icon)
        return icon
        
########################################################################
# Represents UPnP device
class Device(object):
    
#    ROOTXML_TPL = '<root xmlns="urn:schemas-upnp-org:device-1-0">\r\n'
#    ROOTXML_TPL+= '    <specVersion>\r\n'
#    ROOTXML_TPL+= '        <major>1</major>\r\n'
#    ROOTXML_TPL+= '        <minor>0</minor>\r\n'
#    ROOTXML_TPL+= '    </specVersion>\r\n'
#    ROOTXML_TPL+= '%s'
     
    
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
        self.UPC = None
        self.presentationURL = None
        self.baseURL = None
        self.rootDescURL = None
        self.embedded = False
        #self.location = deviceDesc.location
    
    def addDevice(self, device):
        if device.UDN not in self.devices.keys():
            device.parent = self
            self.devices[device.UDN] = device
        
    def addService(self, service):
        if service.serviceId not in self.services.keys():
            service.parent = self
            self.services[service.serviceId] = service

    def addIcon(self, icon):
        self.icons.append(icon)
        
    def getService(self, sid):
        return self.services[sid]
    
    def findService(self, sid):
        pattern = re.compile(sid)
        #print self.services
        for srv in self.services.values():
            #print srv.serviceId
            if pattern.search(srv.serviceId):
                return srv
        
    def genDeviceDesc(self):
        node = etree.Element('device')
        iconList = etree.Element('iconList')
        devList = etree.Element('deviceList')
        srvList = etree.Element('serviceList')
                
        _createNodesFromAttrs(self, ['deviceType', 'friendlyName', 'manufacturer',
                                     'manufacturerURL', 'modelDescription', 'modelNumber',
                                     'modelName', 'modelURL', 'serialNumber', 'UDN', 'UPC',
                                     'presentationURL'],
                              node)
        
        if len(self.icons) > 0:
            for icon in self.icons:
                iconList.append(icon.toXML())
            node.append(iconList)
        
        if len(self.devices) > 0:
            for device in self.devices.values():
                devList.append(device.genDeviceDesc())
            node.append(devList)
                
        if len(self.services) > 0:
            for service in self.services.values():
                srvList.append(service.toXML())
            node.append(srvList)
            
        return node
        
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
        self.controlURL = None
        self.eventSubURL = None
        #self._SCPDURL = None
        self.SCPDURL = None
        #self.actions, self.stateVariables = _parseSCPD(self.device.location.rstrip('/') + '/' + self.SCPDURL.lstrip('/'))
        self.actions = {}
        self.stateVariables = {}
        
    def toXML(self):
        service = etree.Element('service')
        
        _createNodesFromAttrs(self, ['serviceType', 'serviceId', 'controlURL', 'eventSubURL'], service)
        
        scpdNode = etree.Element('SCPDURL')
        scpdNode.text = self.SCPDURL
        service.append(scpdNode)
        
        return service
    
    def genSCPD(self):
        scpd = etree.Element('scpd', xmlns="urn:schemas-upnp-org:service-1-0")
        specVersion = etree.Element('specVersion')
        major = etree.Element('major')
        major.text = '1'
        minor = etree.Element('minor')
        minor.text = '0'
        
        specVersion.append(major)
        specVersion.append(minor)
        scpd.append(specVersion)
        
        actionList = etree.Element('actionList')
        serviceStateTable = etree.Element('serviceStateTable')
        
        if len(self.actions) > 0:
            for action in self.actions.values():
                actionList.append(action.toXML())
            scpd.append(actionList)
        
        if len(self.stateVariables) > 0:
            for variable in self.stateVariables.values():
                serviceStateTable.append(variable.toXML())
            scpd.append(serviceStateTable)
        
        return scpd
        
    
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
     
#    @property
#    def SCPDURL(self):
#        return self._SCPDURL 
#    
#    @SCPDURL.setter
#    def SCPDURL(self, val):
#        base = self._findBaseUrl(val)
#        self.SCPDPath = val
#        self._SCPDURL = base.rstrip('/') + '/' + val.lstrip('/')
        
    
    @property
    def fullSCPDURL(self):
         return self.baseURL.rstrip('/') + '/' + self.SCPDURL.lstrip('/')
     
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
            # urn:upnp-org
            match = re.search(':serviceId:([^:]*)(:(.*))?', self.serviceId)
            if match.group(3) == None:
                return match.group(1)
            else:
                return "%s (v%s)" % (match.group(1), match.group(3)) 
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
                 allowedValueList = None,
                 allowedValueRangeMin = None,
                 allowedValueRangeMax = None,
                 allowedValueRangeStep = None,
                 sendEvents = None,
                 multicast = None,
                 **kwargs):
        self.name = name
        self.dataType = dataType
        self.defaultValue = defaultValue
        if not allowedValueList == None:
            self.allowedValueList = allowedValueList
        else:
            self.allowedValueList = set()
                 
        self.allowedValueRange = Entity()
        self.allowedValueRange.min = allowedValueRangeMin
        self.allowedValueRange.max = allowedValueRangeMax
        self.allowedValueRange.step = allowedValueRangeStep
        self.sendEvents = sendEvents
        self.multicast = multicast
        
        self.value = self.defaultValue
        
        for k, v in zip(kwargs.keys(), kwargs.values()):
            setattr(self, k, v)
            
    def addAllowedValue(self, value):
        self.allowedValueList.add(value)    

    def toXML(self):
        var = etree.Element('stateVariable')
        if self.sendEvents != None:
            var.set('sendEvents', self.sendEvents)
        else:
            var.set('sendEvents', "no")
        
        if self.multicast != None:
            var.set('multicast', self.multicast)
        
        _createNodesFromAttrs(self, ['name', 'dataType', 'defaultValue'], var)
                
        if hasattr(self, 'allowedValueList'):
            valueList = etree.Element('allowedValueList')
            for value in self.allowedValueList:
                node = etree.Element('allowedValue')
                node.text = str(value)
                valueList.append(node)
            
            var.append(valueList)
        
        valueRange = etree.Element('allowedValueRange')
        addValueRange = False
        if self.allowedValueRange.max:
            max = etree.Element('maximum')
            max.text = self.allowedValueRange.max
            valueRange.append(max)
            addValueRange = True 
        
        if self.allowedValueRange.min:
            min = etree.Element('minimum')
            min.text = self.allowedValueRange.min
            valueRange.append(min)
            addValueRange = True
        
        if self.allowedValueRange.step:
            step = etree.Element('step')
            step.text = self.allowedValueRange.step
            valueRange.append(step)
            addValueRange = True
        
        if addValueRange:
            var.append(valueRange)
        return var
        
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
        
    def toXML(self):
        node = etree.Element('argument')
        _createNodesFromAttrs(self, ['name', 'direction', 'retval', 'relatedStateVariable'], node)
        return node

########################################################################
# Represents service action
class Action(object):
    def __init__(self,
                 name=None,
                 argumentList=None):
        self.name = name
        if argumentList == None:
            self.argumentList = {}
        else: 
            self.argumentList = argumentList
            
    def toXML(self):
        action = etree.Element('action')
        _createNodesFromAttrs(self, ['name'], action)
        argumentList = etree.Element('argumentList')
        
        if len(self.argumentList):
            for argument in self.argumentList.values():
                argumentList.append(argument.toXML())
            action.append(argumentList)
        return action
        
    def addArgument(self, arg):
        self.argumentList[arg.name] = arg
    
    @property
    def args(self):
        return self.argumentList.values()
    
    @property
    def argNames(self):
        return self.argumentList.keys() 