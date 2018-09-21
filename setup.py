from setuptools import setup

base_requirements = [
    'protobuf', 'ModestMaps', 'uritemplate', 'requests', 'httmock', 'mock'
    ]

webserver_requirements = ['flask', 'Flask-Cors', 'gunicorn']

dataframe_requirements = [
    'geopandas', 'mercantile', 'Rtree', 'Shapely', 'pandas', 'pyproj', 'Fiona', 'pytz',
    'numpy', 'click-plugins', 'cligj', 'munch', 'python-dateutil'
    ]

setup(
    name = 'sharedstreets',
    version = '0.4.0',
    author = 'Kevin Webb, Denis Carriere, Danny Whalen, Michal Migurski',
    description = 'Python implementation of SharedStreets Reference System',
    license = 'MIT',
    keywords = 'sharedstreets nacto openstreetmap map graph street',
    url = 'https://github.com/sharedstreets/sharedstreets-python',
    packages = ['sharedstreets', 'sharedstreets.tests', 'sharedstreets.dataframe'],
    package_data = {
        'sharedstreets.tests': ['data/*.*'],
        },
    entry_points = {
        'console_scripts': [
            'sharedstreets-read-file = sharedstreets.read:main',
            'sharedstreets-get-tile = sharedstreets.tile:main',
            'sharedstreets-debug-webapp = sharedstreets.webapp:main',
        ]
    },
    install_requires = base_requirements,
    extras_require = {
        'webserver': webserver_requirements,
        'dataframe': dataframe_requirements,
        },
)
