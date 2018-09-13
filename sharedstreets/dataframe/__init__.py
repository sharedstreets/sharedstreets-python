import geopandas
from .. import tile

class Frames:
    ''' Container for dataframes of SharedStreets geometries and intersections.
    '''
    def __init__(self, intersections, geometries):
        self.intersections = intersections
        self.geometries = geometries

class _Feature:
    ''' Simple implementation of __geo_interface__ for GeoDataFrame.from_features().
    '''
    def __init__(self, properties, type, coordinates):
        self.__geo_interface__ = {
            'type': 'Feature', 'properties': properties,
            'geometry': {'type': type, 'coordinates': coordinates},
            }

def get_tile(*args, **kwargs):
    ''' Get a single Frames instance for a tile of SharedStreets entities.
    
        All arguments are passed to tile.get_tile().
    '''
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
