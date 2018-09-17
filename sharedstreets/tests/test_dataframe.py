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
    }

mock_tile.geometries = {
    'NlId': Geometry('NlId', 6, 'NNNN', 'dddd', 'NI', 'IN',
        [-0.000113, 0.000038, 0.000027, 0.000032, 0.000038, -0.000027, 0.000231, -0.000032]),
    }

class TestDataframe (unittest.TestCase):

    def test_get_tile(self):
        
        with mock.patch('sharedstreets.tile.get_tile') as get_tile:
            get_tile.return_value = mock_tile
            frames = dataframe.get_tile(12, 2048, 2048)
        
        self.assertEqual(list(frames.intersections.id), ['NNNN', 'dddd'])
        self.assertEqual(list(frames.intersections.nodeId), [1, 4])
        self.assertEqual(list(frames.geometries.id), ['NlId'])
        self.assertEqual(list(frames.geometries.fromIntersectionId), ['NNNN'])
        self.assertEqual(list(frames.geometries.toIntersectionId), ['dddd'])
    
    def test_get_bbox(self):
        
        with mock.patch('sharedstreets.tile.get_tile') as get_tile:
            get_tile.return_value = mock_tile
            frames = dataframe.get_bbox(-0.00051, -0.00030, 0.00039, 0.00032)
        
        self.assertEqual(list(frames.intersections.id), ['NNNN', 'dddd'])
        self.assertEqual(list(frames.intersections.nodeId), [1, 4])
        self.assertEqual(list(frames.geometries.id), ['NlId'])
        self.assertEqual(list(frames.geometries.fromIntersectionId), ['NNNN'])
        self.assertEqual(list(frames.geometries.toIntersectionId), ['dddd'])
