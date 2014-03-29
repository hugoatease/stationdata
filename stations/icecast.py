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
from xml.dom import minidom
from errors import AdapterFetchingError, AdapterParsingError


class Icecast:
    def __init__(self, url, config):
        self.url = url
        self.config = config
        self.results = {}

    def parseXSPF(self, xml):
        parser = minidom.parseString(xml)
        track = parser.getElementsByTagName('track')[0]

        for node in track.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                key = node.nodeName
                value = node.firstChild.nodeValue
                self.results[key] = value

        return self.results

    def checkTrack(self):
        if self.results.has_key('creator') and self.results.has_key('title'):
            self.results['track'] = self.results['creator'] + ' - ' + self.results['title']

    def parseAnnotation(self):
        if not self.results.has_key('annotation'):
            return False

        annotation = self.results['annotation']
        lines = annotation.split('\n')

        for line in lines:
            separator = line.find(':')
            if separator == -1:
                continue

            key = line[:separator]
            value = line[separator+1:]

            if key != '' and value != '':
                self.results[key] = value

        return True

    def fetch(self):
        try:
            response = requests.get(self.url + '.xspf', timeout=self.config['REQUEST_TIMEOUT'], stream=False)
        except:
            raise AdapterFetchingError(self.url, 'Failed to retrieve XSPF playlist')

        if response.headers['Content-Type'] != 'application/xspf+xml':
            raise AdapterFetchingError(self.url, 'Failed to retrieve XSPF playlist')

        try:
            self.parseXSPF(response.content)
        except:
            raise AdapterParsingError("Failed to parse XSPF playlist")

        self.checkTrack()
        self.parseAnnotation()

        return self.results

name = "Icecast"
adapter = Icecast
mappings = [
    ('name', 'Stream Title'),
    ('genre', 'Stream Genre'),
    ('url', 'info'),
    ('description', 'Stream Description'),
    ('artist', 'creator'),
    ('title', 'title'),
    ('track', 'track')
]

if __name__ == '__main__':
    stream = Icecast('http://radio.108.pl:8006/ambient.ogg')
    print stream.fetch()