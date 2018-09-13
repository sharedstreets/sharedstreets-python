import pandas
import geopandas
from .. import tile

class Addition:

    def __init__(self, new_things):
        self.new_things = new_things
    
    def apply(self, dataframe):
        return dataframe.append(self.new_things, verify_integrity=True)

class Deletion:

    def __init__(self, old_things):
        self.old_things = old_things
    
    def apply(self, dataframe):
        old_ids, deleted_ids, returned_things = set(self.old_things.id), set(), list()
        for thing in dataframe.itertuples():
            if thing.id in old_ids:
                deleted_ids.add(thing.id)
            else:
                returned_things.append(thing)
        
        if len(old_ids) > len(deleted_ids):
            raise ValueError('Missing items in dataframe: {}'.format(old_ids - deleted_ids))
        
        return pandas.DataFrame(returned_things)

things1 = pandas.DataFrame([
    dict(id=1, value='one'),
    dict(id=2, value='two'),
    dict(id=3, value='three'),
    ], index=[1, 2, 3])

things2 = pandas.DataFrame([
    dict(id=4, value='four'),
    ], index=[4])

add_thing4 = Addition(things2)
things3 = add_thing4.apply(things1)
assert len(things3) == 4

try:
    things4 = add_thing4.apply(things3)
except ValueError:
    pass
else:
    assert False

delete_thing4 = Deletion(things2)
things5 = delete_thing4.apply(things3)
assert len(things5) == 3

try:
    things6 = delete_thing4.apply(things1)
except ValueError:
    pass
else:
    assert False

delete_things123 = Deletion(things1)
things7 = delete_things123.apply(add_thing4.apply(things1))
assert len(things7) == 1

class Feature:
    def __init__(self, properties, type, coordinates):
        self.__geo_interface__ = {
            'type': 'Feature', 'properties': properties,
            'geometry': {'type': type, 'coordinates': coordinates},
            }

print('getting')
tile = tile.get_tile(12, 656, 1582) #, data_url_template='http://0.0.0.0:8000/planet-180312-{z}-{x}-{y}.{layer}.6.pbf')

features1 = [
    Feature({
        'id': item.id, 'nodeId': item.nodeId,
        'inboundReferenceIds': item.inboundReferenceIds,
        'outboundReferenceIds': item.outboundReferenceIds,
        }, 'Point', [item.lon, item.lat])
    for item in tile.intersections.values()
    ]

frame1 = geopandas.GeoDataFrame.from_features(features1).set_index('id', drop=False, verify_integrity=True)

print(frame1)

features2 = [
    Feature({
        'id': item.id, 'roadClass': item.roadClass,
        'fromIntersectionId': item.fromIntersectionId,
        'toIntersectionId': item.toIntersectionId,
        'forwardReferenceId': item.forwardReferenceId,
        'backReferenceId': item.backReferenceId,
        }, 'LineString', zip(item.lonlats[0::2], item.lonlats[1::2]))
    for item in tile.geometries.values()
    ]

frame2 = geopandas.GeoDataFrame.from_features(features2).set_index('id', drop=False, verify_integrity=True)

print(frame2)
