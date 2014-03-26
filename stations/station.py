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