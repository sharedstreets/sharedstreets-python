# SharedStreets (Python)

🚧WIP -- commits/comments welcome! 🚧

Python implementation of [SharedStreets Reference System](https://github.com/sharedstreets/sharedstreets-ref-system).

## Install

1.  Clone the SharedStreets-Python git repository and prepare a
    [Python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenv) running Python 3.

2.  Install the `sharedstreets` module, keeping it editable, and run test suite.
    
        pip install --editable .
        python setup.py test

3.  Try downloading a single tile to GeoJSON.

        sharedstreets-get-tile 16 10509 25324 > 16-10509-25324.geojson

4.  Run a debug webserver and request a tile at [`/tile/16/10508/25324.geojson`](http://127.0.0.1:5000/tile/16/10508/25324.geojson).

        sharedstreets-debug-webapp

5.  Run a production webserver under [Gunicorn](http://gunicorn.org/).

        gunicorn sharedstreets.webapp:app

## API
