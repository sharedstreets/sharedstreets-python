import argparse, itertools, sys, json, logging
import ModestMaps.Core, ModestMaps.OpenStreetMap, uritemplate, requests, google.protobuf.message
from google.protobuf.internal.decoder import _DecodeVarint32
from . import sharedstreets_pb2

logger = logging.getLogger(__name__)

# https://github.com/sharedstreets/sharedstreets-ref-system/issues/16
DATA_URL_TEMPLATE, DATA_ZOOM = 'https://tiles.sharedstreets.io/osm/planet-180312/{z}-{x}-{y}.{layer}.6.pbf', 12
data_classes = {
    'reference': sharedstreets_pb2.SharedStreetsReference,
    'intersection': sharedstreets_pb2.SharedStreetsIntersection,
    'geometry': sharedstreets_pb2.SharedStreetsGeometry,
    'metadata': sharedstreets_pb2.SharedStreetsMetadata,
    }

# Used for Mercator projection and tile space
OSM = ModestMaps.OpenStreetMap.Provider()

class Tile:
    ''' Container for dicts of SharedStreets geometries, intersections, references, and metadata.
    '''
    def __init__(self, geometries, intersections, references, metadata):
        self.geometries = geometries
        self.intersections = intersections
        self.references = references
        self.metadata = metadata

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

def get_tile(zoom, x, y, data_url_template=None):
    ''' Get a single Tile instance.
    
        zoom, x, y: Web mercator tile coordinates using OpenStreetMap convention.
        
            https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Zoom_levels
    
        data_url_template: RFC 6570 URI template for upstream protobuf tiles
            with z, x, y, and layer expressions. Default to DATA_URL_TEMPLATE.
            
            https://tools.ietf.org/html/rfc6570#section-2.2)
    '''
    if data_url_template is None:
        data_url_template = DATA_URL_TEMPLATE
    
    # Define lat/lon for filtered area
    tile_coord = ModestMaps.Core.Coordinate(y, x, zoom)
    data_coord = tile_coord.zoomTo(DATA_ZOOM).container()
    tile_sw = OSM.coordinateLocation(tile_coord.down())
    tile_ne = OSM.coordinateLocation(tile_coord.right())
    data_zxy = dict(z=int(data_coord.zoom), x=int(data_coord.column), y=int(data_coord.row))
    
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
    
    return Tile(geometries, intersections, references, metadata)

def geometry_feature(geometry, metadata, id_length):
    '''
    '''
    return {
        'type': 'Feature',
        'role': 'SharedStreets:Geometry',
        'id': geometry.id[:id_length],
        'properties': {
            'id': geometry.id[:id_length],
            'forwardReferenceId': geometry.forwardReferenceId[:id_length],
            'startIntersectionId': geometry.fromIntersectionId[:id_length],
            'backReferenceId': geometry.backReferenceId[:id_length],
            'endIntersectionId': geometry.toIntersectionId[:id_length],
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

def intersection_feature(intersection, id_length):
    '''
    '''
    return {
        'type': 'Feature',
        'role': 'SharedStreets:Intersection',
        'id': intersection.id[:id_length],
        'properties': {
            'id': intersection.id[:id_length],

            'inboundReferenceIds': [id[:id_length] for id in intersection.inboundReferenceIds],
            'outboundReferenceIds': [id[:id_length] for id in intersection.outboundReferenceIds],
            },
        'geometry': {
            'type': 'Point',
            'coordinates': [round_coord(intersection.lon), round_coord(intersection.lat)]
            }
        }

def reference_feature(reference, id_length):
    '''
    '''
    LR0, LR1 = reference.locationReferences
    
    return {
        'role': 'SharedStreets:Reference',
        'id': reference.id[:id_length],
        'geometryId': reference.geometryId[:id_length],
        'formOfWay': reference.formOfWay,
        'locationReferences': [
            {
                'sequence': 0,
                'intersectionId': LR0.intersectionId[:id_length],
                'distanceToNextRef': LR0.distanceToNextRef,
                'point': [round_coord(LR0.lon), round_coord(LR0.lat)],

                'inboundBearing': LR0.inboundBearing,
                'outboundBearing': LR0.outboundBearing,
                },
            {
                'sequence': 1,
                'intersectionId': LR1.intersectionId[:id_length],
                'distanceToNextRef': None,
                'point': [round_coord(LR1.lon), round_coord(LR1.lat)],

                'inboundBearing': None,
                'outboundBearing': None,
                },
            ]
        }

def make_geojson(tile, id_length=32):
    ''' Get a GeoJSON dictionary for a geographic tile.
    
        tile: Tile instance with lists of SharedStreets entities.
        
        id_length: Desired length of SharedStreets ID strings. Normally 32-char
            MD5 hashes, these can be truncated to conserve storage. Default 12.
    '''
    geojson = dict(type='FeatureCollection', features=[], references=[])
    
    for geometry in tile.geometries.values():
        geojson['features'].append(geometry_feature(geometry, tile.metadata[geometry.id], id_length))
        #break
    
    for intersection in tile.intersections.values():
        geojson['features'].append(intersection_feature(intersection, id_length))
        #break
    
    for reference in tile.references.values():
        geojson['references'].append(reference_feature(reference, id_length))
        #break
    
    return geojson

parser = argparse.ArgumentParser(description='Download a tile of SharedStreets data')
parser.add_argument('zoom', type=int, help='Tile zoom')
parser.add_argument('x', type=int, help='Tile X coordinate')
parser.add_argument('y', type=int, help='Tile Y coordinate')

def main():
    args = parser.parse_args()
    geojson = make_geojson(get_tile(args.zoom, args.x, args.y), id_length=32)
    print(json.dumps(geojson, indent=2))
