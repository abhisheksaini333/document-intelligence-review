import hashlib, os, tempfile
from pathlib import Path
MAX_BYTES=8*1024*1024

def identity(data):
    if not isinstance(data,bytes) or not data or len(data)>MAX_BYTES: raise ValueError('Image must contain 1 to 8388608 bytes')
    return hashlib.sha256(data).hexdigest()

def image_type(data):
    identity(data)
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return 'png'
    if data.startswith(b'\xff\xd8\xff'): return 'jpg'
    if data.startswith((b'II*\x00',b'MM\x00*')): return 'tiff'
    raise ValueError('Only PNG, JPEG and TIFF images are supported')
