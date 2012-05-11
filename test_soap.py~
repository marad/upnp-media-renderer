'''
Created on 24-02-2012

@author: morti
'''

import socket

if __name__ == "__main__":
    print "Testing SOAP..."
    
#    soap = SoapClient(location='http://192.168.0.1:1780/control?Layer3Forwarding',
#                      action="urn:schemas-upnp-org:service:Layer3Forwarding:1#",
#                      namespace="uurn:schemas-upnp-org:service:Layer3Forwarding:1",
#                      trace = True,
#                      soap_ns = 'soap',
#                      ns = "u"
#                      )
    
    #response = soap.GetDefaultConnectionService()
    
#    xml = '<?xml version="1.0"?>\
#<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" >\r\n\
#<s:Body>\r\n\
#    <u:SetTarget xmlns:u="urn:schemas-upnp-org:service:SwitchPower:1" >\r\n\
#        <NewTargetValue>true</NewTargetValue>\r\n\
#    </u:SetTarget>\r\n\
#</s:Body>\r\n\
#</s:Envelope>\r\n\r\n'
    
#    msg = 'POST /SwitchPower/Control HTTP/1.0\r\n\
#HOST: 127.0.0.1:43414\r\n\
#SOAPAction: "urn:schemas-upnp-org:service:SwitchPower:1#SetTarget"\r\n\
#CONTENT-LENGTH: '+str(len(xml))+'\r\n\
#USER-AGENT: Linux/123 UPnP/1.1 test/1.0\r\n\
#Content-type: text/xml; charset="UTF-8"\r\n\r\n'

    xml = '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:GetSubnetMask xmlns:u="urn:schemas-upnp-org:service:LANHostConfigManagement:1"></u:GetSubnetMask></s:Body></s:Envelope>'

    msg = 'POST /control?LANHostConfigManagement HTTP/1.0\r\n\
HOST: 192.168.0.1:1780\r\n\
CONTENT-LENGTH: '+ str(len(xml)) +'\r\n\
CONTENT-TYPE: text/xml; charset="utf-8"\r\n\
USER-AGENT: Linux/3.2.6-3.fc16.x86_64 UPNP/1.1 UPnPy/0.1\r\n\
SOAPACTION: "urn:schemas-upnp-org:service:LANHostConfigManagement:1#GetSubnetMask"\r\n\r\n'

    print msg
    
    
    print xml
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("router", 1780))
    s.sendall(msg)
    s.sendall(xml)
    data = s.recv(1024)    
    
    print "Received: ", data
    
    print "Zamykam aplikacje"