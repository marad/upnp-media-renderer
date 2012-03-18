'''
Created on 23-02-2012

@author: morti
'''

import re
import time
import urllib2
from lxml import etree
from upnpy.device import Device, Service, Icon, StateVariable, Action, ActionArgument

def genRootDesc(device):
    root = etree.Element('root', xmlns="urn:schemas-upnp-org:device-1-0")
    specVersion = etree.Element('specVersion')
    major = etree.Element('major')
    major.text = '1'
    minor = etree.Element('minor')
    minor.text = '0'
    
    specVersion.append(major)
    specVersion.append(minor)
    root.append(specVersion)
    root.append(device.genDeviceDesc())
    return root

class Entity(object):
    pass

import traceback
import sys

ns = {
    'dev':'urn:schemas-upnp-org:device-1-0',
    'srv':'urn:schemas-upnp-org:service-1-0'
}

def _xpath(node, xpath):
    list = node.xpath(xpath, namespaces=ns)
    if len(list) > 0:
        return list[0]
    else:
        return None

class SCPDParser(object):
    def parse(self, srv):
        resp = urllib2.urlopen(srv.fullSCPDURL)
        xml = resp.read()
        
        try:
            doc = etree.fromstring(xml)
            
            for variableNode in doc.xpath('srv:serviceStateTable/srv:stateVariable', namespaces=ns):
                variable = StateVariable()
                variable.name           = _xpath(variableNode, 'srv:name/text()')
                variable.dataType       = _xpath(variableNode, 'srv:dataType/text()')
                variable.defaultValue   = _xpath(variableNode, 'srv:defaultValue/text()')            
                for allowedValueNode in variableNode.xpath('srv:allowedValueList/srv:allowedValue', namespaces=ns):
                    #variable.allowedValueList.append( allowedValueNode.text )
                    variable.addAllowedValue(allowedValueNode.text)
                
                variable.allowedValueRange.min = _xpath(variableNode, 'srv:allowedValueRange/srv:minimum')
                variable.allowedValueRange.max = _xpath(variableNode, 'srv:allowedValueRange/srv:maximum')
                variable.allowedValueRange.step = _xpath(variableNode, 'srv:allowedValueRange/srv:step')
                
                variable.sendEvents = _xpath(variableNode, '@sendEvents')
                variable.multicast  = _xpath(variableNode, '@multicast')
                
                #service.stateVariables[variable.name] = variable
                srv.addStateVariable(variable)
            
            for actionNode in doc.xpath('srv:actionList/srv:action', namespaces=ns):
                action = Action()
                action.name = _xpath(actionNode, 'srv:name/text()')
                for argumentNode in actionNode.xpath('srv:argumentList/srv:argument', namespaces=ns):
                    argument = ActionArgument()
                    argument.name       = _xpath(argumentNode, 'srv:name/text()')
                    argument.direction  = _xpath(argumentNode, 'srv:direction/text()')
                    argument.retval     = _xpath(argumentNode, 'srv:retval/text()')
                    argument.relatedStateVariable = _xpath(argumentNode, 'srv:relatedStateVariable/text()')
                    argument.stateVariableRef = srv.stateVariables[argument.relatedStateVariable]
                    #action.argumentList[argument.name] = argument
                    action.addArgument(argument)
                #service.actions[action.name] = action
                srv.addAction(action)
        except:
            traceback.print_exc(file=sys.stderr)

class XmlDescriptionBuilder(object):
    tagNameMatcher = re.compile(r"^({[^}]*})?(.*)$")
    rootDeviceMatcher = re.compile(r"^upnp:rootdevice$")
    deviceTypeMatcher = re.compile(r"^(?:urn:[^:]+:device:)|(?:uuid:.+)")    
    serviceTypeMatcher = re.compile(r"^urn:[^:]+:service:")
    usnMatcher = re.compile(r"^(?P<uuid>uuid:[^:]+)(?:::)?(?P<type>.*)$")
    baseURLMatcher = re.compile(r"^(?P<baseURL>[^:]+://[^:]+:[0-9]+/).+$")
    
    maxAgeMatcher = re.compile(r"max-age=(?P<maxAge>[0-9]+)")
    
    scpdParser = SCPDParser()
    #usnMatcher = re.compile("")
    
    def build(self, headers):
        #print headers['LOCATION']
        if 'ST' in headers:
            type = headers['ST']
        else:
            type = headers['NT']
        
        headers['DEVTYPE'] = type
        
        resp = urllib2.urlopen(headers['LOCATION'])
        xml = resp.read()        
        
        try:
            doc = etree.fromstring(xml)
            rootDeviceNode = doc.xpath("/dev:root/dev:device", namespaces=ns)[0]
            
            entity = None
            if self.rootDeviceMatcher.match(type):
                entity = self.buildRootDevice(rootDeviceNode, headers)
            elif self.deviceTypeMatcher.match(type):
                entity = self.buildDevice(doc, headers)
            elif self.serviceTypeMatcher.match(type):
                entity = self.buildService(doc, headers)
                
            if entity == None:
                print "Error parsing entity for headers:", headers
                return None
                
            if 'CACHE-CONTROL' in headers.keys():
                match = self.maxAgeMatcher.match(headers['CACHE-CONTROL'])
                if match:
                    entity.maxAge = time.time() + int(match.group('maxAge'))
             
            return entity
        except:
            traceback.print_exc(file=sys.stderr)
            return None
    
    def buildRootDevice(self, devNode, headers):
        dev = Device()
        self.parseNode(devNode, dev, ['serviceList', 'deviceList', 'iconList'])
        self.parseIcons(devNode, dev)
        #print "Found device ", dev.friendlyName
        return dev
    
    def buildDevice(self, doc, headers):
        match = self.usnMatcher.match(headers['USN'])
        usn = match.group('uuid')
        
        UDNs = doc.xpath('//dev:UDN[text() = "%s"]' % usn, namespaces=ns )
        if len(UDNs) == 0:
            return None
        devNode = UDNs[0].getparent()
        dev = Device()
        self.parseNode(devNode, dev, ['serviceList', 'deviceList', 'iconList'])
        self.parseIcons(devNode, dev)
        
        try:        
            dev.parentUDN = devNode.xpath("../../dev:UDN/text()", namespaces=ns)[0]
            dev.embedded = True
        except:
            pass
        
        return dev
    
    def buildService(self, doc, headers):
        match = self.usnMatcher.match(headers['USN'])
        devUUID = match.group('uuid')
        serviceType = match.group('type')        
        #print devUUID, serviceId
        serviceTypeNode = doc.xpath('//dev:serviceType[text() = "%s"]' % serviceType, namespaces=ns)[0]
        serviceNode = serviceTypeNode.getparent()
        
        srv = Service()
        self.parseNode(serviceNode, srv)
        srv.parentUDN = devUUID
        
        match = self.baseURLMatcher.match(headers['LOCATION'])
        srv.baseURL = match.group('baseURL')
        
        #print srv.fullSCPDURL    
        #self.parseSCPD(srv)
        self.scpdParser.parse(srv)
        
        #print 'Found service', srv.friendlyName
        return srv
    
    def parseIcons(self, devNode, device):
        iconNodeList = devNode.xpath("dev:iconList/dev:icon", namespaces=ns)
        for iconNode in iconNodeList:
            icon = Icon()
            self.parseNode(iconNode, icon)
            device.addIcon(icon)
            
                
    def parseNode(self, doc, obj, exceptFor=[]):
        """
        Parses an XML node (doc) info Python object OBJ 
        """
        children = doc.getchildren()
        toParse = zip(
            [obj for i in xrange(len(children))],
            children
            )
        while len(toParse):
            obj, node = toParse.pop()
            
            children = node.getchildren()
            
            result = self.tagNameMatcher.match(node.tag)
            tagName = result.group(2)
            
            if tagName == None or tagName in exceptFor:
                continue
            
            if len(children) == 0:
                setattr(obj, tagName, node.text) 
            else:
                nobj = Entity()
                setattr(obj, tagName, nobj)
                toParse.extend(zip(
                    [nobj for i in xrange( len(children) )],
                    children
                    ))     
