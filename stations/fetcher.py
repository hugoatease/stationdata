from station import Station, Mapper

from . import icecast, shoutcast, icymeta
adapters = [icymeta, shoutcast, icecast]

def available_adapters():
    available = []

    for adapter in adapters:
        if hasattr(adapter, 'adapter') and hasattr(adapter, 'mappings'):
            available.append(adapter)

    return available

def adapter_fetch(adapter, url, weights):
    station = Station()

    print "Adaptateur: " + adapter.name

    stream = adapter.adapter(url)
    try:
        result = stream.fetch()
    except:
        print "Erreur critique de l'adaptateur"
        return None

    mapper = Mapper(station, result)
    mapper.mappings(adapter.mappings)
    mapper.map()

    score = station.score(weights)

    print "\tScore: " + str(score)
    return (score, station)

def fetch(url, weights={'track': 4}):
    scores = {}

    for adapter in available_adapters():
        score = adapter_fetch(adapter, url, weights)
        if score == None:
            continue
        else:
            scores[score[0]] = score[1]

    print scores

    best = sorted(scores, key=scores.get, reverse=True)[0]
    result = scores[best]

    print result.export()

    return result