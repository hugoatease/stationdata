from flask import Blueprint, request, jsonify
from stations import fetch, StationError
from functools import wraps
from time import time

api = Blueprint('Stations Data API', __name__)

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

@api.route('/station')
@perf
def station():
    url = request.values['stream']
    score = request.values.get('score')
    requirements = request.values.get('requirements')

    if requirements is not None:
        requirements = requirements.split(',')
        requirements = filter(lambda item: item != '', requirements)

    results = fetch(url, score=score, requirements=requirements)

    return results.export()