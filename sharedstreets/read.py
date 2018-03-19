from __future__ import print_function
import argparse
from google.protobuf.internal.decoder import _DecodeVarint32
from . import sharedstreets_pb2

parser = argparse.ArgumentParser(description='Read sample SharedStreets data')
parser.add_argument('filename', help='Protobuf filename with SharedStreets data')

protobuf_classes = [
    sharedstreets_pb2.SharedStreetsIntersection,
    sharedstreets_pb2.SharedStreetsGeometry,
    sharedstreets_pb2.SharedStreetsReference,
    sharedstreets_pb2.SharedStreetsMetadata,
    ]

def main():
    args = parser.parse_args()
    
    ProtobufClass = None
    
    with open(args.filename, 'rb') as file:
        buffer = file.read()
        n = 0
        while n < len(buffer):
            print('=' * 80)
            print('bytes', n, end=' ')

            msg_len, new_pos = _DecodeVarint32(buffer, n)
            n = new_pos
            msg_buf = buffer[n:n+msg_len]
            n += msg_len
            
            print('to', n, '--', msg_buf[:12].hex(), '...', msg_buf[-12:].hex())

            if ProtobufClass is None:
                for ProtobufClass in protobuf_classes:
                    test_object = ProtobufClass()
                    try:
                        test_object.ParseFromString(msg_buf)
                    except Exception as e:
                        print('not it:', ProtobufClass)
                    else:
                        if ProtobufClass is sharedstreets_pb2.SharedStreetsIntersection:
                            print('maybe:', ProtobufClass)

                            if test_object.nodeId == 0:
                                # probably actually metadata
                                continue
                        
                        print('ok:', ProtobufClass)
                        break
            
            print(' -' * 40)

            object = ProtobufClass()
            object.ParseFromString(msg_buf)
            print(object)
