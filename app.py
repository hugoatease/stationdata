from flask import Flask
from stationsapi import api

app = Flask(__name__)
app.debug = True

app.register_blueprint(api)

if __name__ == '__main__':
    app.run()