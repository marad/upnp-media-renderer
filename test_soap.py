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
    
    xml = '<?xml version="1.0"?>\
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" >\r\n\
<s:Body>\r\n\
    <u:SetTarget xmlns:u="urn:schemas-upnp-org:service:SwitchPower:1" >\r\n\
        <NewTargetValue>true</NewTargetValue>\r\n\
    </u:SetTarget>\r\n\
</s:Body>\r\n\
</s:Envelope>\r\n\r\n'
    
    msg = 'POST /SwitchPower/Control HTTP/1.0\r\n\
HOST: 127.0.0.1:43414\r\n\
SOAPAction: "urn:schemas-upnp-org:service:SwitchPower:1#SetTarget"\r\n\
CONTENT-LENGTH: '+str(len(xml))+'\r\n\
USER-AGENT: Linux/123 UPnP/1.1 test/1.0\r\n\
Content-type: text/xml; charset="UTF-8"\r\n\r\n'

    print msg
    
    
    print xml
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 43414))
    s.sendall(msg)
    s.sendall(xml)
    data = s.recv(1024)    
    
    print "Received: ", data
    
    print "Zamykam aplikacje"