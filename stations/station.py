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

import json

class Station:
    fields = ['name', 'genre', 'url', 'description', 'bitrate', \
              'track', 'artist', 'title']

    def __init__(self, **kwargs):
            self.populate(kwargs)

    def __str__(self):
        return json.dumps(self.export())

    def populate(self, kwargs):
        for field in self.fields:
            if kwargs.has_key(field):
                setattr(self, field, kwargs[field])
            else:
                setattr(self, field, None)

    def __add__(self, other):
        for field in self.fields:
            if getattr(self, field) is None:
                if getattr(other, field) is not None:
                    setattr(self, field, getattr(other, field))

        return self

    def requires(self, fields):
        for field in fields:
            if field in self.fields:
                if getattr(self, field) is None:
                    return False
        return True

    def score(self, weights = {}):
        score = 0

        for field in self.fields:
            if getattr(self, field) != None:
                if weights.has_key(field):
                    score += weights[field]
                else:
                    score += 1

        return score

    def export(self):
        results = {}

        for field in self.fields:
            results[field] = getattr(self, field)

        return results


class Mapper:
    def __init__(self, station, result):
        self.station = station
        self.result = result
        self.registered = []

    def mapping(self, field, adapter_field):
        if not hasattr(self.station, field):
            return False

        if not self.result.has_key(adapter_field):
            return False

        self.registered.append((field, adapter_field))

    def mappings(self, mappings):
        for mapping in mappings:
            self.mapping(mapping[0], mapping[1])

    def map(self):
        for mapping in self.registered:
            setattr(self.station, mapping[0], self.result[mapping[1]])