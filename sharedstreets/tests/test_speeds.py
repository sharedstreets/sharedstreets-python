import unittest, mock, httmock, os, posixpath, ModestMaps.Geo
from .. import speeds_pb2
from .. import speeds

def respond_locally(url, request):
    path_parts = url.path.split(posixpath.sep)
    local_path = os.path.join(os.path.dirname(__file__), 'data', *path_parts[1:])
    
    if os.path.exists(local_path):
        with open(local_path, 'rb') as file:
            return httmock.response(200, file.read())
    
    return httmock.response(404, 'Nope')

class TestTile (unittest.TestCase):

    def test_speeds(self):
        
        speedObservations = []
        
        with open('12-946-1650.speeds.pbf', 'rb') as file:
            fileContent = file.read()
            observations = speeds.flatten_weekly_speed_histogram(fileContent)
            print(observations)
            self.assertEqual(len(observations), 124)
