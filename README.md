# SharedStreets (Python)

🚧WIP -- commits/comments welcome! 🚧

Python implementation of [SharedStreets Reference System](https://github.com/sharedstreets/sharedstreets-ref-system).

## Install

1.  Install [from PyPI with Pip](https://packaging.python.org/tutorials/installing-packages/#installing-from-pypi).
    
        pip install sharedstreets

2.  Try downloading a single tile to GeoJSON.

        sharedstreets-get-tile 16 10509 25324 > 16-10509-25324.geojson

## Use

-   Retrieve a tile and convert to GeoJSON in Python.

        import sharedstreets.tile
        tile = sharedstreets.tile.get_tile(16, 10508, 25324)
        geojson = sharedstreets.tile.make_geojson(tile)

-   Run a debug webserver and request a tile at [`/tile/16/10508/25324.geojson`](http://127.0.0.1:5000/tile/16/10508/25324.geojson).

        sharedstreets-debug-webapp

-   Run a production webserver under [Gunicorn](http://gunicorn.org/).

        gunicorn sharedstreets.webapp:app

-   Read speed data from PBF encoded speed tiles. `flatten_weekly_speed_histogram` returns an array of arrays representing individual histogram bins with the structure `[sharedstreets_referenceId, period_hour_of_week, bin_kmh, observation_count`: 

        import sharedstreets.speeds
        with open('12-946-1650.speeds.pbf', 'rb') as file:
            fileContent = file.read()
            observations = speeds.flatten_weekly_speed_histogram(fileContent)
            print(observations)

-   Read linear references from PBF encoded event tiles. `flatten_binned_events` returns an array of arrays representing individual event counts for linear bins `[sharedstreets_referenceId, referenceLength, numberOfBins, binPosition, dataType, observationCount, observationValue`: 

        import sharedstreets.linear_references
        with open('12-946-1650.events.pbf', 'rb') as file:
            fileContent = file.read()
            observations = linear_references.flatten_binned_events(fileContent)
            print(observations)
            self.assertEqual(len(observations), 89)

## Develop

Install for local development.

1.  Clone the SharedStreets-Python git repository and prepare a
    [Python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenv) running Python 3.

2.  Install the `sharedstreets` module, keeping it editable, and run test suite.
    
        pip install --editable .
        python setup.py test

## Protobufs

Current `.proto` files can can be found at
[sharedstreets/sharedstreets-ref-system](https://github.com/sharedstreets/sharedstreets-ref-system/tree/master/proto).

[Install `protoc`](https://github.com/google/protobuf) and
[follow Python directions](https://developers.google.com/protocol-buffers/docs/reference/python-generated#invocation)
to regenerate `sharedstreets/sharedstreets_pb2.py` if necessary:

    protoc -I=sharedstreets-ref-system/proto/ \
        --python_out=sharedstreets/ \
        sharedstreets-ref-system/proto/sharedstreets.proto
