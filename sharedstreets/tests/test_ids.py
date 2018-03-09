import unittest
from .. import ids

class TestIds (unittest.TestCase):

    def test_generate_hash(self):

        message1 = 'Intersection 110.000000 45.000000'
        message2 = 'Intersection -74.003388 40.634538'
        message3 = 'Intersection -74.004107 40.634060'

        self.assertEqual(ids.generate_hash(message1), '71f34691f182a467137b3d37265cb3b6')
        self.assertEqual(ids.generate_hash(message2), '103c2dbe16d28cdcdcd5e5e253eaa026')
        self.assertEqual(ids.generate_hash(message3), '0f346cb98b5d8f0500e167cb0a390266')

    def test_intersection(self):

        pt1 = [110, 45]
        pt2 = [-74.003388, 40.634538]
        pt3 = [-74.004107, 40.63406]

        self.assertEqual(ids.intersection(pt1), '71f34691f182a467137b3d37265cb3b6')
        self.assertEqual(ids.intersection(pt2), '103c2dbe16d28cdcdcd5e5e253eaa026')
        self.assertEqual(ids.intersection(pt3), '0f346cb98b5d8f0500e167cb0a390266')

    def test_geometry(self):

        line1 = [[110, 45], [115, 50], [120, 55]]
        line2 = [[-74.007568359375, 40.75239562988281], [-74.00729370117188, 40.753089904785156]]
        line3 = [[-74.00778198242188, 40.72457504272461], [-74.0076675415039, 40.72519302368164]]

        self.assertEqual(ids.geometry(line1), 'ce9c0ec1472c0a8bab3190ab075e9b21')
        self.assertEqual(ids.geometry(line2), '02aa80dc9c72ea4175bfb10c05e5a2b9')
        self.assertEqual(ids.geometry(line3), '58ae3bdd54f99e0331a8cb147557adcc')
