import geopandas
from .. import tile

class Frames:
    ''' Container for dataframes of SharedStreets geometries and intersections.
    '''
    def __init__(self, intersections, geometries):
        self.intersections = intersections
        self.geometries = geometries

class _Feature:
    def __init__(self, properties, type, coordinates):
        self.__geo_interface__ = {
            'type': 'Feature', 'properties': properties,
            'geometry': {'type': type, 'coordinates': coordinates},
            }
def get_tile(zoom, x, y, data_url_template=None):
    ''' Get a single Frames instance.
    
        Arguments are passed to tile.get_tile().
        
        zoom, x, y: Web mercator tile coordinates using OpenStreetMap convention.
        data_url_template: RFC 6570 URI template for upstream protobuf tiles.
    '''
    T = tile.get_tile(zoom, x, y, data_url_template)

    features1 = [
        _Feature({
            'id': item.id, 'nodeId': item.nodeId,
            'inboundReferenceIds': item.inboundReferenceIds,
            'outboundReferenceIds': item.outboundReferenceIds,
            }, 'Point', [item.lon, item.lat])
        for item in T.intersections.values()
        ]

    features2 = [
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
    iframe = geopandas.GeoDataFrame.from_features(features1).set_index('id', **kwargs)
    gframe = geopandas.GeoDataFrame.from_features(features2).set_index('id', **kwargs)
    
    return Frames(iframe, gframe)
