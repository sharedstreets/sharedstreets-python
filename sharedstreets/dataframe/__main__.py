import pandas
import geopandas
from . import get_tile, get_bbox

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

print('getting')
#frames = get_tile(12, 656, 1582, data_url_template='http://0.0.0.0:8000/planet-180312-{z}-{x}-{y}.{layer}.6.pbf')
#frames = get_bbox(-122.26482, 37.79760, -122.24636, 37.81286, data_url_template='http://0.0.0.0:8000/planet-180312-{z}-{x}-{y}.{layer}.6.pbf')
frames = get_bbox(-122.26713, 37.84947, -122.25177, 37.86960) #, data_url_template='http://0.0.0.0:8000/planet-180312-{z}-{x}-{y}.{layer}.6.pbf')
print(frames.intersections)
print(frames.geometries)
