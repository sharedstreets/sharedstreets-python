import flask, flask_cors, argparse
from . import tile

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route('/')
def get_index():
    return 'YO'

@app.route('/tile/<int:zoom>/<int:x>/<int:y>.geojson')
def get_tile(zoom, x, y):
    return flask.jsonify(tile.make_geojson(tile.get_tile(zoom, x, y)))

parser = argparse.ArgumentParser(description='Run a local SharedStreets tile webserver')

def main():
    parser.parse_args()
    app.run(debug=True)    
