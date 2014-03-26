#!/usr/bin/python
import requests
from xml.dom import minidom
from errors import AdapterFetchingError, AdapterParsingError

class Icecast:
    def __init__(self, url):
        self.url = url
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
            response = requests.get(self.url + '.xspf', timeout=5)
        except:
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