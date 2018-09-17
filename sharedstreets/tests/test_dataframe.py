import unittest, mock, collections
from .. import dataframe

Geometry = collections.namedtuple('Geometry', ['id', 'roadClass',
    'fromIntersectionId', 'toIntersectionId', 'forwardReferenceId',
    'backReferenceId', 'lonlats'])

Intersection = collections.namedtuple('Intersection', ['id', 'nodeId',
    'inboundReferenceIds', 'outboundReferenceIds', 'lon', 'lat'])

class TestDataframe (unittest.TestCase):

    def test_get_tile(self):
        
        with mock.patch('sharedstreets.tile.get_tile') as get_tile:
            mock_tile = get_tile.return_value
            mock_tile.intersections = {
                'NNNN': Intersection('NNNN', 1, ['IN'], ['NI'], -0.000113, 0.000038),
                'dddd': Intersection('dddd', 4, ['NI'], ['IN'], 0.000231, -0.000032),
                }
            mock_tile.geometries = {
                'NlId': Geometry('NlId', 6, 'NNNN', 'dddd', 'NI', 'IN',
                    [-0.000113, 0.000038, 0.000027, 0.000032, 0.000038, -0.000027, 0.000231, -0.000032]),
                }
            
            # N -0.000113 0.000038
            # l 0.000027 0.000032
            # I 0.000038 -0.000027
            # d 0.000231 -0.000032
        
            frames = dataframe.get_tile(12, 2048, 2048)
        
        print(frames.intersections)
        print(frames.geometries)
