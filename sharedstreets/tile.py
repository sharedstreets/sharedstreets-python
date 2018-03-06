import argparse
import ModestMaps.Core, uritemplate
from . import sharedstreets_pb2

# https://github.com/sharedstreets/sharedstreets-ref-system/issues/16
data_url_template, data_zoom = 'http://tiles.sharedstreets.io/{z}-{x}-{y}.{layer}.pbf', 12
data_classes = {
    'reference': sharedstreets_pb2.SharedStreetsReference,
    'intersection': sharedstreets_pb2.SharedStreetsIntersection,
    'geometry': sharedstreets_pb2.SharedStreetsGeometry,
    'metadata': sharedstreets_pb2.SharedStreetsMetadata,
    }

def get_tile(zoom, x, y):
    '''
    '''
    tile_coord = ModestMaps.Core.Coordinate(y, x, zoom)
    data_coord = tile_coord.zoomTo(data_zoom).container()
    
    print(tile_coord, data_coord)
    
    data_zxy = dict(z=data_coord.zoom, x=data_coord.column, y=data_coord.row)
    
    for (layer, data_class) in data_classes.items():
        print(uritemplate.expand(data_url_template, layer=layer, **data_zxy))
        print(data_class)

parser = argparse.ArgumentParser(description='Download a tile of SharedStreets data')
parser.add_argument('zoom', type=int, help='Tile zoom')
parser.add_argument('x', type=int, help='Tile X coordinate')
parser.add_argument('y', type=int, help='Tile Y coordinate')

def main():
    args = parser.parse_args()
    get_tile(args.zoom, args.x, args.y)
