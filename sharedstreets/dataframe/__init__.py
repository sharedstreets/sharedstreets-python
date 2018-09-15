import itertools
import functools
import operator
import logging
import collections
import geopandas
import mercantile
from .. import tile

# Container for dataframes of SharedStreets geometries and intersections.
Frames = collections.namedtuple('Frames', ['intersections', 'geometries'])

class _Feature:
    ''' Simple implementation of __geo_interface__ for GeoDataFrame.from_features().
    '''
    def __init__(self, properties, type, coordinates):
        self.__geo_interface__ = {
            'type': 'Feature', 'properties': properties,
            'geometry': {'type': type, 'coordinates': coordinates},
            }

def _union_dataframes(dataframe1, dataframe2):
    ''' Return union of two DataFrames with no repeated IDs.
    
        Ensure that IDs aren't repeated so DataFrame.append() does not complain.
    '''
    seen_ids, new_rows = set(dataframe1.index), list()

    for (id, row) in dataframe2.iterrows():
        if id not in seen_ids:
            seen_ids.add(id)
            new_rows.append(row)
    
    return dataframe1.append(new_rows, verify_integrity=True)

def _combine_geodataframes(minlon, minlat, maxlon, maxlat, geodataframes):
    ''' Clip bbox from multiple GeoDataFrames and return their union.

    Union all frames together after using GeoDataFrame.cx to clip bounds
    '''
    return functools.reduce(_union_dataframes,
        [frame.cx[minlon:maxlon, minlat:maxlat] for frame in geodataframes])

def _collect_dataframe_rows(ids, dataframes):
    ''' Collect identified rows from multiple DataFrames into one and return it.
    '''
    remaining_ids, new_rows = set(ids), list()
    
    for dataframe in dataframes:
        for (id, row) in dataframe.iterrows():
            if id in remaining_ids:
                remaining_ids.remove(id)
                new_rows.append(row)
    
    # Initialize an empty frame that new rows can be appended to
    empty_dataframe = dataframes[0].iloc[0:0]
    
    return empty_dataframe.append(new_rows, verify_integrity=True)

def get_bbox(minlon, minlat, maxlon, maxlat, data_url_template=None):
    ''' Get a single Frames instance of SharedStreets entities in an area.
    '''
    ul = mercantile.tile(minlon, maxlat, tile.DATA_ZOOM)
    lr = mercantile.tile(maxlon, minlat, tile.DATA_ZOOM)
    
    tile_frames = [
        get_tile(tile.DATA_ZOOM, x, y, data_url_template) for (x, y)
        in itertools.product(range(ul.x, lr.x+1), range(ul.y, lr.y+1))
        ]
    
    geometries = _combine_geodataframes(minlon, minlat, maxlon, maxlat,
        [frames.geometries for frames in tile_frames])
    
    ids = set(geometries.fromIntersectionId) | set(geometries.toIntersectionId)

    intersections = _collect_dataframe_rows(ids,
        [frames.intersections for frames in tile_frames])

    return Frames(intersections, geometries)

def get_tile(*args, **kwargs):
    ''' Get a single Frames instance for a tile of SharedStreets entities.
    
        All arguments are passed to tile.get_tile().
    '''
    logging.debug('get_tile', args, kwargs)
    T = tile.get_tile(*args, **kwargs)

    ifeatures = [
        _Feature({
            'id': item.id, 'nodeId': item.nodeId,
            'inboundReferenceIds': item.inboundReferenceIds,
            'outboundReferenceIds': item.outboundReferenceIds,
            }, 'Point', [item.lon, item.lat])
        for item in T.intersections.values()
        ]

    gfeatures = [
        _Feature({
            'id': item.id, 'roadClass': item.roadClass,
            'fromIntersectionId': item.fromIntersectionId,
            'toIntersectionId': item.toIntersectionId,
            'forwardReferenceId': item.forwardReferenceId,
            'backReferenceId': item.backReferenceId,
            }, 'LineString', zip(item.lonlats[0::2], item.lonlats[1::2]))
        for item in T.geometries.values()
        ]

    kwargs = dict(drop=False, verify_integrity=True)
    iframe = geopandas.GeoDataFrame.from_features(ifeatures).set_index('id', **kwargs)
    gframe = geopandas.GeoDataFrame.from_features(gfeatures).set_index('id', **kwargs)
    
    return Frames(iframe, gframe)
