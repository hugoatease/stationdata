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
from errors import AdapterParsingError, AdapterFetchingError


class ICYMeta:
    def __init__(self, url, config):
        self.url = url
        self.config = config
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

    def parseData(self, meta,   response):
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

                if self.position > self.config['STREAM_MAX_BYTES']:
                    response.close()
                    raise AdapterParsingError('Maximum stream bytes reached')

    def fetch(self):
        try:
            response = requests.get(self.url, stream=True, headers={'Icy-MetaData': '1'})
        except:
            raise AdapterFetchingError(self.url, "Can't open stream")

        try:
            meta = self.parseHTTPMeta(response)
        except:
            raise AdapterParsingError("Stream header parsing failed")

        try:
            self.parseData(meta, response)
        except:
            raise AdapterParsingError("Stream metadata parsing failed")

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
    print stream.fetch()