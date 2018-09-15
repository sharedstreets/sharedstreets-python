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

def _combine_geometries(minlon, minlat, maxlon, maxlat, geometry_frames):
    ''' Clip bbox from multiple geometry dataframes and return their union.
    
        Ensure that IDs aren't repeated so GeoDataFrame.append() does not complain.
    '''
    def union_geoframes(frame1, frame2):
        ''' Return union of two frames with no repeated IDs.
        '''
        seen_ids, new_rows = set(frame1.index), list()
    
        for (id, row) in frame2.iterrows():
            if id not in seen_ids:
                seen_ids.add(id)
                new_rows.append(row)
        
        return frame1.append(new_rows, verify_integrity=True)
    
    # Union all frames together after using GeoDataFrame.cx to clip bounds
    return functools.reduce(union_geoframes, [
        frame.cx[minlon:maxlon, minlat:maxlat] for frame in geometry_frames
        ])

def _collect_intersections(ids, intersection_frames):
    ''' Collect named intersections from multiple dataframes into one dataframe.
    '''
    remaining_ids, new_rows = set(ids), list()
    
    for frame in intersection_frames:
        for (id, row) in frame.iterrows():
            if id in remaining_ids:
                remaining_ids.remove(id)
                new_rows.append(row)
    
    # Initialize an empty frame that new rows can be appended to
    empty_frame = intersection_frames[0].iloc[0:0]
    
    return empty_frame.append(new_rows, verify_integrity=True)

def get_bbox(minlon, minlat, maxlon, maxlat, data_url_template=None):
    ''' Get a single Frames instance of SharedStreets entities in an area.
    '''
    ul = mercantile.tile(minlon, maxlat, tile.DATA_ZOOM)
    lr = mercantile.tile(maxlon, minlat, tile.DATA_ZOOM)
    
    tile_frames = [
        get_tile(tile.DATA_ZOOM, x, y, data_url_template) for (x, y)
        in itertools.product(range(ul.x, lr.x+1), range(ul.y, lr.y+1))
        ]
    
    geometries_frame = _combine_geometries(minlon, minlat, maxlon, maxlat,
        [frames.geometries for frames in tile_frames])
    
    logging.debug(geometries_frame.dtypes)
    logging.debug(geometries_frame.shape)
    
    ids = set(geometries_frame.fromIntersectionId) | set(geometries_frame.toIntersectionId)

    intersections_frame = _collect_intersections(ids,
        [frames.intersections for frames in tile_frames])

    logging.debug(intersections_frame.dtypes)
    logging.debug(intersections_frame.shape)
    
    return Frames(intersections_frame, geometries_frame)

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
