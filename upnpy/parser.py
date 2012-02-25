'''
Created on 23-02-2012

@author: morti
'''

import re
import urllib2
#from xml.dom.minidom import parseString
from lxml import etree
from upnpy.device import Device, Service, Icon, StateVariable, Action, ActionArgument

class DeviceDescriptionParser(object):
    
    def __init__(self):
        self.namespaces = {
                'dev':'urn:schemas-upnp-org:device-1-0',
                'srv':'urn:schemas-upnp-org:service-1-0'
        }
    
    def _xpath(self, node, xpath):
        list = node.xpath(xpath, namespaces=self.namespaces)
        if len(list) > 0:
            return list[0]
        else:
            return None

    def _createDevice(self, baseURL, deviceNode):
        dev = Device()
        dev.deviceType          = self._xpath(deviceNode, 'dev:deviceType/text()')
        dev.friendlyName        = self._xpath(deviceNode, 'dev:friendlyName/text()')
        dev.manufacturer        = self._xpath(deviceNode, 'dev:manufacturer/text()')
        dev.manufacturerURL     = self._xpath(deviceNode, 'dev:manufacturerURL/text()')
        dev.modelDescription    = self._xpath(deviceNode, 'dev:modelDescription/text()')
        dev.modelName           = self._xpath(deviceNode, 'dev:modelName/text()')
        dev.modelNumber         = self._xpath(deviceNode, 'dev:modelNumber/text()')
        dev.modelURL            = self._xpath(deviceNode, 'dev:modelURL/text()')
        dev.serialNumber        = self._xpath(deviceNode, 'dev:serialNumber/text()')
        dev.UDN                 = self._xpath(deviceNode, 'dev:UDN/text()')
        dev.UPC                 = self._xpath(deviceNode, 'dev:UPC/text()')
        dev.presentationURL     = self._xpath(deviceNode, 'dev:presentationURL/text()')
        dev.baseURL = baseURL
        
        # Icon list
        for iconNode in deviceNode.xpath('dev:iconList/dev:icon', namespaces=self.namespaces):
            icon = Icon()
            icon.mimetype       = self._xpath(iconNode, 'dev:mimetype/text()')
            icon.width          = self._xpath(iconNode, 'dev:width/text()')
            icon.height         = self._xpath(iconNode, 'dev:height/text()')
            icon.depth          = self._xpath(iconNode, 'dev:depth/text()')
            icon.url            = self._xpath(iconNode, 'dev:url/text()')
            dev.icons.append(icon)
            
        # Service list
        for serviceNode in deviceNode.xpath('dev:serviceList/dev:service', namespaces=self.namespaces):
            service = self._createService(baseURL, serviceNode)
            dev.services[service.serviceId] = service
        
        # Sub-devices
        for subDeviceNode in deviceNode.xpath('dev:deviceList/dev:device', namespaces=self.namespaces):
            subDev = self._createDevice(baseURL, subDeviceNode)
            dev.devices[subDev.UDN] = subDev
            
        return dev
        
    def _createService(self, baseURL, serviceNode):        
        service = Service()
        service.baseURL     = baseURL
        service.serviceType = self._xpath(serviceNode, 'dev:serviceType/text()')
        service.serviceId   = self._xpath(serviceNode, 'dev:serviceId/text()')
        service.SCPDURL     = self._xpath(serviceNode, 'dev:SCPDURL/text()')
        service.controlURL  = self._xpath(serviceNode, 'dev:controlURL/text()')
        service.eventSubURL = self._xpath(serviceNode, 'dev:eventSubURL/text()')
        
        response = urllib2.urlopen(service.SCPDURL)
        doc = etree.fromstring(response.read())
        
        for variableNode in doc.xpath('srv:serviceStateTable/srv:stateVariable', namespaces=self.namespaces):
            variable = StateVariable()
            variable.name           = self._xpath(variableNode, 'srv:name/text()')
            variable.dataType       = self._xpath(variableNode, 'srv:dataType/text()')
            variable.defaultValue   = self._xpath(variableNode, 'srv:defaultValue/text()')            
            for allowedValueNode in variableNode.xpath('srv:allowedValueList/srv:allowedValue', namespaces=self.namespaces):
                variable.allowedValueList.append( allowedValueNode.text )
            
            variable.allowedValueRange.min = self._xpath(variableNode, 'srv:allowedValueRange/srv:minimum')
            variable.allowedValueRange.max = self._xpath(variableNode, 'srv:allowedValueRange/srv:maximum')
            variable.allowedValueRange.step = self._xpath(variableNode, 'srv:allowedValueRange/srv:step')
            
            variable.sendEvents = self._xpath(variableNode, '@sendEvents')
            variable.multicast  = self._xpath(variableNode, '@multicast')
            
            #service.stateVariables[variable.name] = variable
            service.addStateVariable(variable)
        
        for actionNode in doc.xpath('srv:actionList/srv:action', namespaces=self.namespaces):
            action = Action()
            action.name = self._xpath(actionNode, 'srv:name/text()')
            for argumentNode in actionNode.xpath('srv:argumentList/srv:argument', namespaces=self.namespaces):
                argument = ActionArgument()
                argument.name       = self._xpath(argumentNode, 'srv:name/text()')
                argument.direction  = self._xpath(argumentNode, 'srv:direction/text()')
                argument.retval     = self._xpath(argumentNode, 'srv:retval/text()')
                argument.relatedStateVariable = self._xpath(argumentNode, 'srv:relatedStateVariable/text()')
                argument.stateVariableRef = service.stateVariables[argument.relatedStateVariable]
                #action.argumentList[argument.name] = argument
                action.addArgument(argument)
            #service.actions[action.name] = action
            service.addAction(action)
        return service
    
    ########################################################################
    # Parse root device description xml
    # Args: 
    #     data - dictionary from SSDP headers
    # Returns device object
    
    def parse(self, rootDeviceDescURL):
        
#        if data == None or data['LOCATION'] == None:
#            return None
#        
#        rootDeviceDescURL = data['LOCATION']
        
        response = urllib2.urlopen(rootDeviceDescURL)
        xml = response.read()    
        doc = etree.fromstring(xml)
            
        
        #deviceNode = doc.xpath("dev:device", namespaces=self.namespaces)
        deviceNode = self._xpath(doc, 'dev:device')
        baseURL = re.search('^[^:]+://[^/]*', rootDeviceDescURL).group(0)
        
        device = self._createDevice(baseURL, deviceNode)
        device.rootDescURL = rootDeviceDescURL
        return device

      