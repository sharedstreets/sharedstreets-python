import unittest, mock, httmock, os, posixpath, ModestMaps.Geo
from .. import tile

def respond_locally(url, request):
    path_parts = url.path.split(posixpath.sep)
    local_path = os.path.join(os.path.dirname(__file__), 'data', *path_parts[1:])
    
    if os.path.exists(local_path):
        with open(local_path, 'rb') as file:
            return httmock.response(200, file.read())
    
    return httmock.response(404, 'Nope')

class TestTile (unittest.TestCase):

    def test_iter_objects_intersection(self):
        
        with httmock.HTTMock(respond_locally):
            intersections = tile.iter_objects('http://example.com/intersection.pbf',
                tile.data_classes['intersection'])
            i1, i2, i3 = list(intersections)
        
        self.assertEqual(i1.id, '8018a9f7b6e318308200068ebb6068a4')
        self.assertEqual((i1.lon, i1.lat), (-122.2907957, 37.8537091))

        self.assertEqual(i2.id, '80863f59547240f6d5c06856f7e318ce')
        self.assertEqual((i2.lon, i2.lat), (-122.2606473, 37.813789))

        self.assertEqual(i3.id, '80e533ecdcc667e37c9473c4b6fdb03d')
        self.assertEqual((i3.lon, i3.lat), (-122.28473890000001, 37.840128500000006))

    def test_iter_objects_geometry(self):
        
        with httmock.HTTMock(respond_locally):
            geometries = tile.iter_objects('http://example.com/geometry.pbf',
                tile.data_classes['geometry'])
            g1, g2, g3 = list(geometries)
        
        self.assertEqual(g1.id, '80832506185371acf24df519ce271d31')
        self.assertEqual(g1.lonlats[0:2], [-122.2951692, 37.8564139])
        self.assertEqual(len(g1.lonlats), 10)

        self.assertEqual(g2.id, '80a8a7c120332bfb679f877472c9c18d')
        self.assertEqual(g2.lonlats[0:2], [-122.2926467, 37.7971926])
        self.assertEqual(len(g2.lonlats), 4)

        self.assertEqual(g3.id, '82b5776e9fcce1c64a431a14bd59b15d')
        self.assertEqual(g3.lonlats[0:2], [-122.28428740000001, 37.827691900000005])
        self.assertEqual(len(g3.lonlats), 16)

    def test_iter_objects_reference(self):
        
        with httmock.HTTMock(respond_locally):
            references = tile.iter_objects('http://example.com/reference.pbf',
                tile.data_classes['reference'])
            r1, r2, r3 = list(references)
        
        self.assertEqual(r1.id, '21f5b48ac661484b3f9c8ba840831709')
        self.assertEqual(r1.geometryId, '04d743e5b9a8a77719b581d99b0d1f4c')
        self.assertEqual(len(r1.locationReferences), 2)
        self.assertEqual(r1.locationReferences[0].intersectionId, '88ce4ccabde624261fcc145d7e9cec95')
        self.assertEqual(r1.locationReferences[1].intersectionId, 'ea1b255a2f0657d7c6ac5d901e7bbe24')
        
        self.assertEqual(r2.id, 'e821c707f37104544c9d79f28f565ba4')
        self.assertEqual(r2.geometryId, '04d743e5b9a8a77719b581d99b0d1f4c')
        self.assertEqual(len(r2.locationReferences), 2)
        self.assertEqual(r2.locationReferences[0].intersectionId, 'ea1b255a2f0657d7c6ac5d901e7bbe24')
        self.assertEqual(r2.locationReferences[1].intersectionId, '88ce4ccabde624261fcc145d7e9cec95')
        
        self.assertEqual(r3.id, '48bc7f50cf29440884e85e6e64cc1530')
        self.assertEqual(r3.geometryId, 'eca330faf57285b5941aa715bba337c6')
        self.assertEqual(len(r3.locationReferences), 2)
        self.assertEqual(r3.locationReferences[0].intersectionId, '38d5bb092bc572bd305a7812f0c8c0bf')
        self.assertEqual(r3.locationReferences[1].intersectionId, '0ad982f6c3e46b256115742f49da8da5')

    def test_iter_objects_metadata(self):
        
        with httmock.HTTMock(respond_locally):
            metadata = tile.iter_objects('http://example.com/metadata.pbf',
                tile.data_classes['metadata'])
            m1, m2, m3 = list(metadata)
        
        self.assertEqual(m1.geometryId, '809235c41285600f26c3bb390a99f344')
        self.assertEqual(len(m1.osmMetadata.waySections), 1)
        self.assertEqual(m1.osmMetadata.waySections[0].wayId, 461285181)
        
        self.assertEqual(m2.geometryId, '802f5d102ca9351370a7baa86b0a3ffe')
        self.assertEqual(len(m2.osmMetadata.waySections), 1)
        self.assertEqual(m2.osmMetadata.waySections[0].wayId, 461128457)
        
        self.assertEqual(m3.geometryId, '8072396f545c82abcb34bd5124c4ba6d')
        self.assertEqual(len(m3.osmMetadata.waySections), 1)
        self.assertEqual(m3.osmMetadata.waySections[0].wayId, 21466380)
    
    def test_is_inside(self):
        
        with httmock.HTTMock(respond_locally):
            geometries = tile.iter_objects('http://example.com/geometry.pbf',
                tile.data_classes['geometry'])
            
            # 11th Street between Castro & MLK
            geometry = next(geometries)
        
        # Corner to the northeast near MLK & 15th
        ne = ModestMaps.Geo.Location(37.806469, -122.275192)

        # Box completely enclosing the geometry from Castro & 10th
        sw1 = ModestMaps.Geo.Location(37.80355359456757, -122.2787976264954)
        self.assertTrue(tile.is_inside(sw1, ne, geometry))
        
        # Box overlapping the geometry bbox from north side of 11th
        sw2 = ModestMaps.Geo.Location(37.80440977021365, -122.2777998447418)
        self.assertTrue(tile.is_inside(sw2, ne, geometry))
        
        # Box outside the geometry bbox from MLK & 13th
        sw3 = ModestMaps.Geo.Location(37.80554567109770, -122.2763836383820)
        self.assertFalse(tile.is_inside(sw3, ne, geometry))
    
    @mock.patch('sharedstreets.tile.iter_objects')
    def test_get_tile(self, iter_objects):
    
        everything = mock.Mock()
        everything.id = 'everything'
        everything.geometryId = 'everything'
        everything.fromIntersectionId = 'everything'
        everything.lonlats = [-122.27120, 37.80437, -122.27182, 37.80598]
        iter_objects.return_value = [everything, everything]
    
        geometries, intersections, references = tile.get_tile(16, 10509, 25324)
        
        self.assertEqual(len(geometries), 1)
        self.assertEqual(len(intersections), 1)
        self.assertEqual(len(references), 1)