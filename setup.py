from setuptools import setup

setup(
    name = 'sharedstreets',
    version = '0.2.1',
    author = 'Kevin Webb, Denis Carriere, Michal Migurski',
    description = 'Python implementation of SharedStreets Reference System',
    license = 'MIT',
    keywords = 'sharedstreets nacto openstreetmap map graph street',
    url = 'https://github.com/sharedstreets/sharedstreets-python',
    packages = ['sharedstreets', 'sharedstreets.tests'],
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
    install_requires = [
        'protobuf==3.5.1',
        'ModestMaps==1.4.7',
        'uritemplate==3.0.0',
        'requests==2.18.4',
        'flask==0.12.2',
        'Flask-Cors==3.0.3',
        'gunicorn==19.7.1',
        'httmock==1.2.6',
        'mock==2.0.0',
        ],
    extras_require = {
        'local': [
            'geopandas==0.4.0',
            'Shapely==1.6.4.post2',
            'pandas==0.23.4',
            'pyproj==1.9.5.1',
            'Fiona==1.7.13',
            'pytz==2018.5',
            'numpy==1.15.1',
            'click-plugins==1.0.3',
            'cligj==0.4.0',
            'munch==2.3.2',
            'python-dateutil==2.7.3',
            ]
        },
)
