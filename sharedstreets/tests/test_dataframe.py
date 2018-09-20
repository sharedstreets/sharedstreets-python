import unittest, mock, collections
from .. import dataframe

Geometry = collections.namedtuple('Geometry', ['id', 'roadClass',
    'fromIntersectionId', 'toIntersectionId', 'forwardReferenceId',
    'backReferenceId', 'lonlats'])

Intersection = collections.namedtuple('Intersection', ['id', 'nodeId',
    'inboundReferenceIds', 'outboundReferenceIds', 'lon', 'lat'])

mock_tile = mock.Mock()

mock_tile.intersections = {
    'NNNN': Intersection('NNNN', 1, ['IN'], ['NI'], -0.000113, 0.000038),
    'dddd': Intersection('dddd', 4, ['NI'], ['IN'], 0.000231, -0.000032),
    'OOOO': Intersection('OOOO', 5, ['LO'], ['OL'], -122.2589, 37.8116),
    'land': Intersection('land', 8, ['OL'], ['LO'], -122.2341, 37.8068),
    }

mock_tile.geometries = {
    'NlId': Geometry('NlId', 6, 'NNNN', 'dddd', 'NI', 'IN',
        [-0.000113, 0.000038, 0.000027, 0.000032, 0.000038, -0.000027, 0.000231, -0.000032]),
    'Okld': Geometry('Okld', 6, 'OOOO', 'land', 'OL', 'LO',
        [-122.2589, 37.8116, -122.2472, 37.8119, -122.2468, 37.8068, -122.2341, 37.8068]),
    }

class TestDataframe (unittest.TestCase):

    def test_get_tile(self):
        
        with mock.patch('sharedstreets.tile.get_tile') as get_tile:
            get_tile.return_value = mock_tile
            frames = dataframe.get_tile(12, 2048, 2048)
        
        self.assertEqual(set(frames.intersections.id), {'NNNN', 'dddd', 'OOOO', 'land'})
        self.assertEqual(set(frames.intersections.nodeId), {1, 4, 5, 8})
        self.assertEqual(set(frames.geometries.id), {'NlId', 'Okld'})
        self.assertEqual(set(frames.geometries.fromIntersectionId), {'NNNN', 'OOOO'})
        self.assertEqual(set(frames.geometries.toIntersectionId), {'dddd', 'land'})

    def test_get_bbox(self):
        
        with mock.patch('sharedstreets.tile.get_tile') as get_tile:
            get_tile.return_value = mock_tile
            frames = dataframe.get_bbox(-0.00051, -0.00030, 0.00039, 0.00032)
        
        self.assertEqual(set([mock_call[1][:3] for mock_call in get_tile.mock_calls]),
            {(12, 2047, 2047), (12, 2047, 2048), (12, 2048, 2047), (12, 2048, 2048)},
            'Should look for four tiles around Null Island')
        
        self.assertEqual(set(frames.intersections.id), {'NNNN', 'dddd'})
        self.assertEqual(set(frames.intersections.nodeId), {1, 4})
        self.assertEqual(set(frames.geometries.id), {'NlId'})
        self.assertEqual(set(frames.geometries.fromIntersectionId), {'NNNN'})
        self.assertEqual(set(frames.geometries.toIntersectionId), {'dddd'})
