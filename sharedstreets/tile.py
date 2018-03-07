import argparse, itertools, sys
import ModestMaps.Core, ModestMaps.OpenStreetMap, uritemplate, requests
from google.protobuf.internal.decoder import _DecodeVarint32
from . import sharedstreets_pb2

# https://github.com/sharedstreets/sharedstreets-ref-system/issues/16
data_url_template, data_zoom = 'https://tiles.sharedstreets.io/{z}-{x}-{y}.{layer}.pbf', 12
data_classes = {
    'reference': sharedstreets_pb2.SharedStreetsReference,
    'intersection': sharedstreets_pb2.SharedStreetsIntersection,
    'geometry': sharedstreets_pb2.SharedStreetsGeometry,
    'metadata': sharedstreets_pb2.SharedStreetsMetadata,
    }

# Used for Mercator projection and tile space
OSM = ModestMaps.OpenStreetMap.Provider()

def iter_objects(url, DataClass):
    ''' Generate a stream of objects from the protobuf URL.
    '''
    response, position = requests.get(url), 0
    print('Got', len(response.content), 'bytes:',
        repr(response.content[:32]), file=sys.stderr)

    while position < len(response.content):
        message_length, new_position = _DecodeVarint32(response.content, position)
        position = new_position
        message = response.content[position:position+message_length]
        position += message_length

        object = DataClass()
        object.ParseFromString(message)
        yield object

def is_inside(southwest, northeast, geometry):
    ''' Return True if the geometry bbox is inside a location pair bbox.
    '''
    lons = [geometry.lonlats[i] for i in range(0, len(geometry.lonlats), 2)]
    lats = [geometry.lonlats[i] for i in range(1, len(geometry.lonlats), 2)]
    
    if max(lons) < southwest.lon or northeast.lon < min(lons):
        return False
    
    elif max(lats) < southwest.lat or northeast.lat < min(lats):
        return False
    
    return True

def get_tile(zoom, x, y):
    ''' Get geometries, intersections, and references inside a tile.
    '''
    # Define lat/lon for filtered area
    tile_coord = ModestMaps.Core.Coordinate(y, x, zoom)
    data_coord = tile_coord.zoomTo(data_zoom).container()
    tile_sw = OSM.coordinateLocation(tile_coord.down())
    tile_ne = OSM.coordinateLocation(tile_coord.right())
    data_zxy = dict(z=data_coord.zoom, x=data_coord.column, y=data_coord.row)
    
    print(tile_coord, data_coord, tile_sw, tile_ne, file=sys.stderr)
    
    # Filter geometries within the selected tile
    geom_data_url = uritemplate.expand(data_url_template, layer='geometry', **data_zxy)
    geometries = {geom.id: geom for geom in iter_objects(geom_data_url,
        data_classes['geometry']) if is_inside(tile_sw, tile_ne, geom)}
    
    print(len(geometries), 'geometries', file=sys.stderr)
    
    # Get intersections attached to one of the filtered geometries
    inter_data_url = uritemplate.expand(data_url_template, layer='intersection', **data_zxy)

    intersection_ids = {id for id in itertools.chain(*[(geom.fromIntersectionId,
        geom.toIntersectionId) for geom in geometries.values()])}
    intersections = {inter.id: inter for inter in iter_objects(inter_data_url,
        data_classes['intersection']) if inter.id in intersection_ids}
    
    print(len(intersections), 'intersections', file=sys.stderr)
    
    # Get references attached to one of the filtered geometries
    ref_data_url = uritemplate.expand(data_url_template, layer='reference', **data_zxy)
    references = {ref.id: ref for ref in iter_objects(ref_data_url,
        data_classes['reference']) if ref.geometryId in geometries}
    
    print(len(references), 'references', file=sys.stderr)
    
    return geometries, intersections, references

def geometry_feature(geometry):
    '''
    '''
    return {
        'type': 'Feature',
        'role': 'SharedStreets:Geometry',
        'id': geometry.id,
        'properties': {
            'id': geometry.id,
            'forwardReferenceId': geometry.forwardReferenceId,
            'startIntersectionId': geometry.fromIntersectionId,
            'backReferenceId': geometry.backReferenceId,
            'endIntersectionId': geometry.toIntersectionId,
            'roadClass': geometry.roadClass,
            },
        'geometry': {
            'type': 'LineString',
            'coordinates': [[x, y] for (x, y) in zip(
                [geometry.lonlats[i] for i in range(0, len(geometry.lonlats), 2)],
                [geometry.lonlats[i] for i in range(1, len(geometry.lonlats), 2)]
                )
                ]
            }
        }

def intersection_feature(intersection):
    '''
    '''
    return {
        'type': 'Feature',
        'role': 'SharedStreets:Intersection',
        'id': intersection.id,
        'properties': {
            'id': intersection.id,
            'inboundSegmentIds': intersection.inboundReferenceIds,
            'outboundSegmentIds': intersection.outboundReferenceIds,
            },
        'geometry': {
            'type': 'Point',
            'coordinates': [intersection.lon, intersection.lat]
            }
        }

def make_geojson(geometries, intersections, references):
    '''
    '''
    features = []
    
    for geometry in geometries.values():
        features.append(geometry_feature(geometry))
        break
    
    for intersection in intersections.values():
        features.append(intersection_feature(intersection))
        break
    
    import pprint; pprint.pprint(features)

parser = argparse.ArgumentParser(description='Download a tile of SharedStreets data')
parser.add_argument('zoom', type=int, help='Tile zoom')
parser.add_argument('x', type=int, help='Tile X coordinate')
parser.add_argument('y', type=int, help='Tile Y coordinate')

def main():
    args = parser.parse_args()
    geometries, intersections, references = get_tile(args.zoom, args.x, args.y)
    
    make_geojson(geometries, intersections, references)
