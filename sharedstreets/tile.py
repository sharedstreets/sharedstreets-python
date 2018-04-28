import argparse, itertools, sys, json, logging
import ModestMaps.Core, ModestMaps.OpenStreetMap, uritemplate, requests, google.protobuf.message
from google.protobuf.internal.decoder import _DecodeVarint32
from . import sharedstreets_pb2

logger = logging.getLogger(__name__)

# https://github.com/sharedstreets/sharedstreets-ref-system/issues/16
data_url_template, data_zoom = 'https://tiles.sharedstreets.io/osm/planet-180312/{z}-{x}-{y}.{layer}.6.pbf', 12
data_classes = {
    'reference': sharedstreets_pb2.SharedStreetsReference,
    'intersection': sharedstreets_pb2.SharedStreetsIntersection,
    'geometry': sharedstreets_pb2.SharedStreetsGeometry,
    'metadata': sharedstreets_pb2.SharedStreetsMetadata,
    }

# Used for Mercator projection and tile space
OSM = ModestMaps.OpenStreetMap.Provider()

def truncate_id(id):
    ''' Truncate SharedStreets hash to save space.
    '''
    return id[:12]

def round_coord(float):
    ''' Round a latitude or longitude to appropriate length.
    '''
    return round(float, 7)

def iter_objects(url, DataClass):
    ''' Generate a stream of objects from the protobuf URL.
    '''
    response, position = requests.get(url), 0
    logger.debug('Got {} bytes: {}'.format(len(response.content), repr(response.content[:32])))

    if response.status_code not in range(200, 299):
        logger.debug('Got HTTP {}'.format(response.status_code))
        return

    while position < len(response.content):
        message_length, new_position = _DecodeVarint32(response.content, position)
        position = new_position
        message = response.content[position:position+message_length]
        position += message_length

        try:
            object = DataClass()
            object.ParseFromString(message)
        except google.protobuf.message.DecodeError:
            # Empty tile? Shrug.
            continue
        else:
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
    
    logger.debug((tile_coord, data_coord, tile_sw, tile_ne))
    
    # Filter geometries within the selected tile
    geom_data_url = uritemplate.expand(data_url_template, layer='geometry', **data_zxy)
    geometries = {geom.id: geom for geom in iter_objects(geom_data_url,
        data_classes['geometry']) if is_inside(tile_sw, tile_ne, geom)}
    
    logger.debug('{} geometries'.format(len(geometries)))
    
    # Get intersections attached to one of the filtered geometries
    inter_data_url = uritemplate.expand(data_url_template, layer='intersection', **data_zxy)

    intersection_ids = {id for id in itertools.chain(*[(geom.fromIntersectionId,
        geom.toIntersectionId) for geom in geometries.values()])}
    intersections = {inter.id: inter for inter in iter_objects(inter_data_url,
        data_classes['intersection']) if inter.id in intersection_ids}
    
    logger.debug('{} intersections'.format(len(intersections)))
    
    # Get references attached to one of the filtered geometries
    ref_data_url = uritemplate.expand(data_url_template, layer='reference', **data_zxy)
    references = {ref.id: ref for ref in iter_objects(ref_data_url,
        data_classes['reference']) if ref.geometryId in geometries}
    
    logger.debug('{} references'.format(len(references)))
    
    # Get metadata attached to one of the filtered geometries
    md_data_url = uritemplate.expand(data_url_template, layer='metadata', **data_zxy)
    metadata = {md.geometryId: md for md in iter_objects(md_data_url,
        data_classes['metadata']) if md.geometryId in geometries}
    
    logger.debug('{} metadata'.format(len(metadata)))
    
    return geometries, intersections, references, metadata

def geometry_feature(geometry, metadata):
    '''
    '''
    return {
        'type': 'Feature',
        'role': 'SharedStreets:Geometry',
        'id': truncate_id(geometry.id),
        'properties': {
            'id': truncate_id(geometry.id),
            'forwardReferenceId': truncate_id(geometry.forwardReferenceId),
            'startIntersectionId': truncate_id(geometry.fromIntersectionId),
            'backReferenceId': truncate_id(geometry.backReferenceId),
            'endIntersectionId': truncate_id(geometry.toIntersectionId),
            'roadClass': geometry.roadClass,
            'osmName': str(metadata.osmMetadata.name),
            },
        'geometry': {
            'type': 'LineString',
            'coordinates': [[x, y] for (x, y) in zip(
                [round_coord(geometry.lonlats[i]) for i in range(0, len(geometry.lonlats), 2)],
                [round_coord(geometry.lonlats[i]) for i in range(1, len(geometry.lonlats), 2)]
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
        'id': truncate_id(intersection.id),
        'properties': {
            'id': truncate_id(intersection.id),

            'inboundReferenceIds': list(map(truncate_id, intersection.inboundReferenceIds)),
            'outboundReferenceIds': list(map(truncate_id, intersection.outboundReferenceIds)),
            },
        'geometry': {
            'type': 'Point',
            'coordinates': [round_coord(intersection.lon), round_coord(intersection.lat)]
            }
        }

def reference_feature(reference):
    '''
    '''
    LR0, LR1 = reference.locationReferences
    
    return {
        'role': 'SharedStreets:Reference',
        'id': truncate_id(reference.id),
        'geometryId': truncate_id(reference.geometryId),
        'formOfWay': reference.formOfWay,
        'locationReferences': [
            {
                'sequence': 0,
                'intersectionId': truncate_id(LR0.intersectionId),
                'distanceToNextRef': LR0.distanceToNextRef,
                'point': [round_coord(LR0.lon), round_coord(LR0.lat)],

                'inboundBearing': LR0.inboundBearing,
                'outboundBearing': LR0.outboundBearing,
                },
            {
                'sequence': 1,
                'intersectionId': truncate_id(LR1.intersectionId),
                'distanceToNextRef': None,
                'point': [round_coord(LR1.lon), round_coord(LR1.lat)],

                'inboundBearing': None,
                'outboundBearing': None,
                },
            ]
        }

def make_geojson(geometries, intersections, references, metadata):
    '''
    '''
    geojson = dict(type='FeatureCollection', features=[], references=[])
    
    for geometry in geometries.values():
        geojson['features'].append(geometry_feature(geometry, metadata[geometry.id]))
        #break
    
    for intersection in intersections.values():
        geojson['features'].append(intersection_feature(intersection))
        #break
    
    for reference in references.values():
        geojson['references'].append(reference_feature(reference))
        #break
    
    return geojson

parser = argparse.ArgumentParser(description='Download a tile of SharedStreets data')
parser.add_argument('zoom', type=int, help='Tile zoom')
parser.add_argument('x', type=int, help='Tile X coordinate')
parser.add_argument('y', type=int, help='Tile Y coordinate')

def main():
    args = parser.parse_args()
    geometries, intersections, references, metadata = get_tile(args.zoom, args.x, args.y)
    geojson = make_geojson(geometries, intersections, references, metadata)
    print(json.dumps(geojson, indent=2))
