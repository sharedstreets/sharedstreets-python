from setuptools import setup

setup(
    name = 'sharedstreets',
    version = '0.1.1',
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
)
