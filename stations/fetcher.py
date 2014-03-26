from station import Station, Mapper

from . import icecast, shoutcast, icymeta

class Fetcher:
    adapters = [icymeta, shoutcast, icecast]

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

        stream = adapter.adapter(self.url)
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
            except:
                pass

        return result

    def fetch_until_score(self, score, weights = {}):
        result = Station()

        for adapter in self.available_adapters:
            print 'TEST'
            try:
                result += self.adapter_fetch(adapter)
                if result.score(weights) >= score:
                    break
            except:
                pass

        return result

    def fetch_requirements(self, requirements):
        result = Station()

        for adapter in self.available_adapters:
            try:
                result += self.adapter_fetch(adapter)
                if result.requires(requirements):
                    break
            except:
                pass

        return result

    def fetch(self, score=None, requirements=None, weights=[]):
        if score is None and requirements is None:
            return self.fetch_all()

        if score is not None:
            return self.fetch_until_score(score, weights)

        if requirements is not None:
            return self.fetch_requirements(requirements)


def fetch(url):
    return Fetcher(url).fetch()