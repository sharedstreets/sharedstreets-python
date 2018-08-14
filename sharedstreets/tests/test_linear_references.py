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
        filename = '12-946-1650.events.pbf'
        with open(filename, 'rb') as file:
            fileContent = file.read()
            observations = linear_references.load_binned_events(fileContent)
            self.assertEqual(len(observations), 31)

            test_output_filename = '__test__' + filename
            try:
                os.remove(test_output_filename)
            except OSError:
                pass

            newFile = open(test_output_filename, "wb")
            linear_references.generate_pbf(newFile, observations) 
            newFile.close()

            with open(test_output_filename, 'rb') as file:
                fileContent = file.read()
                test_observations = linear_references.load_binned_events(fileContent)
                self.assertEqual(len(test_observations), 31)

      

            flattened_count = 0
            for observation in observations:
                for item in observation.flatten():
                    flattened_count += 1
                    print(item)
            
            self.assertEqual(flattened_count, 89)

            flattened_count = 0
            for observation in observations:
                observation.filter(1)
                for item in observation.flatten():
                    flattened_count += 1
                    print(item)

            self.assertEqual(flattened_count, 89)

            flattened_count = 0
            for observation in observations:
                observation.filter(2)
                for item in observation.flatten():
                    flattened_count += 1
                    print(item)

            self.assertEqual(flattened_count, 0)