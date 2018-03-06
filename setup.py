from setuptools import setup

setup(
    name = 'sharedstreets',
    version = '0.0.0',
    author = 'Kevin Webb, Denis Carriere, Michal Migurski',
    description = 'Python implementation of SharedStreets Reference System',
    license = 'MIT',
    keywords = 'sharedstreets nacto openstreetmap map graph street',
    url = 'https://github.com/sharedstreets/sharedstreets-python',
    packages = ['sharedstreets'],
    entry_points = {
        'console_scripts': [
            'sharedstreets-test = sharedstreets.test:main',
            'sharedstreets-tile = sharedstreets.tile:main',
        ]
    },
    install_requires = ['protobuf==3.5.1', 'ModestMaps==1.4.7', 'uritemplate==3.0.0'],
)
