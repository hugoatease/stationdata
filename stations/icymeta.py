#!/usr/bin/python
import requests
from station import Mapper, Station

class ICYMeta:
    def __init__(self, url):
        self.url = url
        self.buffers = {'meta' : '', 'audio' : ''}
        self.results = {}
        self.meta = ''
        self.position = 0
        self.metalen = None
        self.metapos = 0


    def parseICYMeta(self):
        lines = self.buffers['meta'].split('\n')
        if lines[0] != 'ICY 200 OK\r':
            return None

        for line in lines[1:]:
            separator = line.find(':')
            if separator == -1:
                continue

            key = line[:separator]
            value = line[separator+1:-1]

            if key != '' and value != '':
                self.results[key] = value

        return True

    def parseHTTPMeta(self, response):
        if len(response.headers) > 0:
            for key in response.headers.keys():
                self.results[key] = response.headers[key]
            return True
        else:
            return False

    def parseAudio(self, chunk):
        if not self.results.has_key('icy-metaint'):
            return False

        if self.metalen != None:
            if self.metapos < self.metalen:
                self.meta += chunk
                self.metapos += 1
            else:
                return False

        if self.position == int(self.results['icy-metaint']):
            self.metalen = ord(chunk) * 16

        self.position += 1
        self.buffers['audio'] += chunk

        return True

    def parseAudioMeta(self):
        for item in self.meta.split(';'):
            parts = item.split("='")
            if len(parts) == 2:
                self.results[parts[0]] = parts[1][:-1]

        return self.results

    def fetch(self):
        response = requests.get(self.url, stream=True, headers={'Icy-MetaData': '1'})

        meta = self.parseHTTPMeta(response)

        for chunk in response.iter_content():
            if not meta:
                self.buffers['meta'] += chunk
                if '\r\n\r\n' in self.buffers['meta']:
                    meta = True
                    self.parseICYMeta()
            else:
                if not self.parseAudio(chunk):
                    response.close()
                    self.parseAudioMeta()
                    break

        return self.results

name = "ICY Metadata"
adapter = ICYMeta
mappings = [
    ('name', 'icy-name'),
    ('genre', 'icy-genre'),
    ('url', 'icy-url'),
    ('bitrate', 'icy-br'),
    ('track', 'StreamTitle')
]

if __name__ == '__main__':
    stream = ICYMeta('http://ice.somafm.com/groovesalad')
    result = stream.fetch()
    station = Station()
    mapper = Mapper(station, result)
    mapper.mappings(mappings)
    mapper.map()
    print station.export()
    print station.score({'track' : 4})