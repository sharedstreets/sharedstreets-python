import argparse, sys
import ModestMaps.Core, uritemplate, requests
from google.protobuf.internal.encoder import _VarintBytes
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

def iter_objects(url, DataClass):
    '''
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

def get_tile(zoom, x, y):
    '''
    '''
    tile_coord = ModestMaps.Core.Coordinate(y, x, zoom)
    data_coord = tile_coord.zoomTo(data_zoom).container()
    
    print(tile_coord, data_coord)
    
    data_zxy = dict(z=data_coord.zoom, x=data_coord.column, y=data_coord.row)
    
    for (layer, DataClass) in data_classes.items():
        data_url = uritemplate.expand(data_url_template, layer=layer, **data_zxy)
        print(data_url, DataClass)
        for obj in iter_objects(data_url, DataClass):
            print(obj)
            break

parser = argparse.ArgumentParser(description='Download a tile of SharedStreets data')
parser.add_argument('zoom', type=int, help='Tile zoom')
parser.add_argument('x', type=int, help='Tile X coordinate')
parser.add_argument('y', type=int, help='Tile Y coordinate')

def main():
    args = parser.parse_args()
    get_tile(args.zoom, args.x, args.y)
