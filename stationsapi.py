from flask import Blueprint, current_app, request, jsonify
from werkzeug.contrib.cache import MemcachedCache

from stations import Fetcher, StationError

from functools import wraps
from time import time

api = Blueprint('Stations Data API', __name__)

cache = MemcachedCache(['127.0.0.1:11211'])

def fetcher_init(url):
    fetcher = Fetcher(url)

    timeout = current_app.config.get('STATIONS_REQUEST_TIMEOUT')
    if timeout is not None:
        fetcher.config['REQUEST_TIMEOUT'] = timeout

    max_bytes = current_app.config.get('STATIONS_MAX_BYTES')
    if max_bytes is not None:
        fetcher.config['STREAM_MAX_BYTES'] = max_bytes

    return fetcher


def cachekey(request):
    key = request.path

    for value in request.values.keys():
        key += value + request.values[value]

    return key

def perf(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        data = {}

        begin = time()

        try:
            data['results'] = function(*args, **kwargs)
            data['error'] = False
        except StationError as error:
            data['error'] = True
            data['reason'] = str(error)

        data['process_time'] = time() - begin

        return jsonify(data)

    return wrapper

def caching(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        key = cachekey(request)

        data = cache.get(key)
        if data is not None:
            return data

        data = function(*args, **kwargs)
        cache.set(key, data, timeout=20)

        return data

    return wrapper

@api.route('/station')
@perf
@caching
def station():
    url = request.values['stream']
    score = request.values.get('score')
    requirements = request.values.get('requirements')

    if requirements is not None:
        requirements = requirements.split(',')
        requirements = filter(lambda item: item != '', requirements)

    fetcher = fetcher_init(url)
    results = fetcher.fetch(score=score, requirements=requirements)

    return results.export()