import unittest, mock, httmock, os, posixpath, ModestMaps.Geo
from .. import speeds_pb2
from .. import linear_references

def respond_locally(url, request):
    path_parts = url.path.split(posixpath.sep)
    local_path = os.path.join(os.path.dirname(__file__), 'data', *path_parts[1:])
    
    if os.path.exists(local_path):
        with open(local_path, 'rb') as file:
            return httmock.response(200, file.read())
    
    return httmock.response(404, 'Nope')

class TestTile (unittest.TestCase):

    def test_linear_references(self):

        with open('12-946-1650.events.pbf', 'rb') as file:
            fileContent = file.read()
            observations = linear_references.flatten_binned_events(fileContent)
            print(observations)
            self.assertEqual(len(observations), 89)
