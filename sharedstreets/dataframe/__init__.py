import itertools
import functools
import operator
import logging
import collections
import geopandas
import mercantile
from shapely.geometry import box
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

def _make_frames(intersections, geometries, bounds=None):
    ''' Return a Frames instance for lists of SharedStreets entities.
    '''
    ifeatures = [
        _Feature({
            'id': item.id, 'nodeId': item.nodeId,
            'inboundReferenceIds': item.inboundReferenceIds,
            'outboundReferenceIds': item.outboundReferenceIds,
            }, 'Point', [item.lon, item.lat])
        for item in intersections
        ]

    gfeatures = [
        _Feature({
            'id': item.id, 'roadClass': item.roadClass,
            'fromIntersectionId': item.fromIntersectionId,
            'toIntersectionId': item.toIntersectionId,
            'forwardReferenceId': item.forwardReferenceId,
            'backReferenceId': item.backReferenceId,
            }, 'LineString', zip(item.lonlats[0::2], item.lonlats[1::2]))
        for item in geometries
        ]

    def clip_bbox(gdf):
        if bounds is None:
            return gdf
        index = list(gdf.sindex.intersection(bounds))
        return gdf.iloc[index]

    def make_frame(features):
        gdf = geopandas.GeoDataFrame.from_features(features, crs={'init': 'epsg:4326'})
        return gdf.set_index('id', drop=False, verify_integrity=True)

    intersectionsdf = clip_bbox(make_frame(ifeatures))
    geometriesdf = clip_bbox(make_frame(gfeatures))

    return Frames(intersectionsdf, geometriesdf)

def get_bbox(minlon, minlat, maxlon, maxlat, data_url_template=None):
    ''' Get a single Frames instance of SharedStreets entities in an area.
    '''
    bounds = (minlon, minlat, maxlon, maxlat)
    ul = mercantile.tile(minlon, maxlat, tile.DATA_ZOOM)
    lr = mercantile.tile(maxlon, minlat, tile.DATA_ZOOM)
    
    tiles = [
        tile.get_tile(tile.DATA_ZOOM, x, y, data_url_template) for (x, y)
        in itertools.product(range(ul.x, lr.x+1), range(ul.y, lr.y+1))
        ]
    
    all_geometries = functools.reduce(lambda d, t: dict(d, **t.geometries), tiles, {})
    all_intersections = functools.reduce(lambda d, t: dict(d, **t.intersections), tiles, {})

    return _make_frames(all_intersections.values(), all_geometries.values(), bounds)

def get_tile(*args, **kwargs):
    ''' Get a single Frames instance for a tile of SharedStreets entities.
    
        All arguments are passed to tile.get_tile().
    '''
    logging.debug('get_tile', args, kwargs)
    T = tile.get_tile(*args, **kwargs)

    return _make_frames(T.intersections.values(), T.geometries.values())
