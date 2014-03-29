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

from station import Station, Mapper
from errors import StationError

from . import icecast, shoutcast, icymeta


class Fetcher:
    adapters = [shoutcast, icecast, icymeta]
    config = {
        'REQUEST_TIMEOUT': 5,
        'STREAM_MAX_BYTES': 5120000
    }

    def __init__(self, url):
        self.url = url
        self.available_adapters = []
        self.get_available_adapters()

    def get_available_adapters(self):
        for adapter in self.adapters:
            if hasattr(adapter, 'adapter') and hasattr(adapter, 'mappings'):
                self.available_adapters.append(adapter)

        return self.available_adapters

    def adapter_fetch(self, adapter):
        current = Station()

        stream = adapter.adapter(self.url, self.config)
        result = stream.fetch()

        mapper = Mapper(current, result)
        mapper.mappings(adapter.mappings)
        mapper.map()

        return current

    def fetch_all(self):
        result = Station()

        for adapter in self.available_adapters:
            try:
                result += self.adapter_fetch(adapter)
            except StationError as error:
                print error

        return result

    def fetch_until_score(self, score, weights = {}):
        result = Station()

        for adapter in self.available_adapters:
            print 'TEST'
            try:
                result += self.adapter_fetch(adapter)
                if result.score(weights) >= score:
                    break
            except StationError as error:
                print error

        return result

    def fetch_requirements(self, requirements):
        result = Station()

        for adapter in self.available_adapters:
            try:
                result += self.adapter_fetch(adapter)
                if result.requires(requirements):
                    break
            except StationError as error:
                print error

        return result

    def fetch(self, score=None, requirements=None, weights=[]):
        if score is None and requirements is None:
            return self.fetch_all()

        if score is not None:
            return self.fetch_until_score(score, weights)

        if requirements is not None:
            return self.fetch_requirements(requirements)


def fetch(url, *args, **kwargs):
    return Fetcher(url).fetch(*args, **kwargs)