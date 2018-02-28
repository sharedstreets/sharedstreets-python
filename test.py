# SharedStreets used length delimited messages for tile files. 
# The Python PBF lib doesn't contain helper functions to do this, so borrowing example from:
# https://www.datadoghq.com/blog/engineering/protobuf-parsing-in-python/

# to run test grab sample tile file via:
# https://tiles.sharedstreets.io/12-1188-1976.reference.pbf 

from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
import sharedstreets_pb2 as ss

ss.SharedStreetsReference()

with open('12-1188-1976.reference.pbf', 'rb') as f:
    buf = f.read()
    n = 0
    while n < len(buf):
        msg_len, new_pos = _DecodeVarint32(buf, n)
        n = new_pos
        msg_buf = buf[n:n+msg_len]
        n += msg_len
        reference = ss.SharedStreetsReference()
        reference.ParseFromString(msg_buf)
        print reference        

	
