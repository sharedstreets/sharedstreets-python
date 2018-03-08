import flask
from . import tile

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return 'YO'

@app.route('/tile/<int:zoom>/<int:x>/<int:y>.geojson')
def get_tile(zoom, x, y):
    return flask.jsonify(tile.make_geojson(*tile.get_tile(zoom, x, y)))

def main():
    app.run(debug=True)    
