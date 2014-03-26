#!/usr/bin/python
import requests
import urlparse
from xml.dom import minidom

class Shoutcast:
    def __init__(self, url):
        self.url = url
        self.results = {}

    def getSID(self):
        response = requests.get(urlparse.urljoin(self.url, 'index.html'), timeout=5)
        query = urlparse.parse_qs(urlparse.urlparse(response.url).query)
        if not query.has_key('sid'):
            return None
        else:
            return int(query['sid'][0])

    def getStatus(self, sid):
        url = urlparse.urljoin(self.url, 'stats?sid=' + str(sid))
        response = requests.get(url, timeout=5)
        return response.content

    def parseStatus(self, xml):
        parser = minidom.parseString(xml)
        server = parser.getElementsByTagName('SHOUTCASTSERVER')[0]

        for node in server.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                key = node.nodeName
                value = node.firstChild.nodeValue
                self.results[key] = value

        return self.results


    def fetch(self):
        sid = self.getSID()
        xml = self.getStatus(sid)
        self.parseStatus(xml)

        return self.results

name = "Shoutcast"
adapter = Shoutcast
mappings = [
    ('name', 'SERVERTITLE'),
    ('genre', 'SERVERGENRE'),
    ('url', 'SERVERURL'),
    ('bitrate', 'BITRATE'),
    ('track', 'SONGTITLE')
]

if __name__ == '__main__':
    stream = Shoutcast('http://94.23.40.70:8010/')
    print stream.fetch()