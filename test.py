'''
Created on 16-03-2012

@author: morti
'''

from urllib import urlopen
from lxml import etree
from upnpy.xmlutil import XmlDescriptionParser, Entity


ns = {
    'dev':'urn:schemas-upnp-org:device-1-0',
    'srv':'urn:schemas-upnp-org:service-1-0'
}

if __name__ == '__main__':
    resp = urlopen('http://192.168.0.1:1780/InternetGatewayDevice.xml')
    xml = resp.read()
    
    doc = etree.fromstring(xml)
    doc = doc.xpath('/dev:root/dev:device', namespaces=ns)[0]
    
    par = XmlDescriptionParser()
    
    ent = Entity()
    
    exc = ['serviceList', 'deviceList']
    #print par.tagNameMatcher.match('hello').group(2)
    
    #par._parseNode(doc, ent, exc)
    par.parseNode(doc, ent, exc)
    
    print repr( [ x for x in dir( ent ) if not x.startswith('__') ] )
    
    print dir(ent)
    
    import re
    usnMatcher = re.compile(r"^(?P<uuid>uuid:[^:]+)(::)?(?P<type>.*)$")
    
    usn = "uuid:3bebb45e-a030-44fa-8365-f21701021271::urn:schemas-upnp-org:device:DimmableLight:1"
    usn2 = "uuid:3bebb45e-a030-44fa-8365-f21701021271::upnp:rootdevice"
    
    match = usnMatcher.match(usn)
    print match.groupdict()
    
    match2 = usnMatcher.match(usn2)    
    print match2.groupdict()
    
    url = "http://192.168.0.114:47452/RootDevice0x81f180.xml"
    baseURLMatcher = re.compile(r"^(?P<baseURL>[^:]+://[^:]+:[0-9]+/).+$")
    
    match = baseURLMatcher.match(url)
    print match.group('baseURL')
    
    
    