import hashlib

def geometry(line):
    pts = ['{x:.6f} {y:.6f}'.format(x=x, y=y) for (x, y) in line]
    message = 'Geometry {}'.format(' '.join(pts))
    return generate_hash(message)

def intersection(pt):
    message = 'Intersection {x:.6f} {y:.6f}'.format(x=pt[0], y=pt[1])
    return generate_hash(message)

def generate_hash(string):
    return hashlib.md5(string.encode('ascii')).hexdigest()
