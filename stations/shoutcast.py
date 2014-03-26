#!/usr/bin/env python

# Copyright (c) 2014 - Hugo Caille
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import requests
import urlparse
from xml.dom import minidom
from errors import AdapterFetchingError, AdapterParsingError

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
        try:
            sid = self.getSID()
        except:
            raise AdapterFetchingError(self.url, 'Unable to retrieve Station ID')

        try:
            xml = self.getStatus(sid)
        except:
            raise AdapterFetchingError(self.url, 'Unable to retrieve station status')

        try:
            self.parseStatus(xml)
        except:
            raise AdapterParsingError('Unable to parse station status')

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