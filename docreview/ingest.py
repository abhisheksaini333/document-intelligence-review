import hashlib, os, tempfile
from pathlib import Path
MAX_BYTES=8*1024*1024

def validate_image(data):
    import io,warnings
    from PIL import Image
    image_type(data)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                width,height=image.size;pages=getattr(image,'n_frames',1)
                if width*height>20_000_000 or pages>20: raise ValueError('Page or pixel limit exceeded')
                image.verify();return {'width':width,'height':height,'pages':pages}
    except Exception as exc: raise ValueError('Invalid image or unsupported dimensions') from exc

def save_image(directory,data):
    suffix=image_type(data); digest=identity(data)
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    target=directory/(digest+'.'+suffix)
    if target.exists():
        if target.is_symlink() or target.read_bytes()!=data: raise ValueError('Stored content failed integrity check')
        return target
    fd,name=tempfile.mkstemp(prefix='.upload-',dir=directory)
    try:
        with os.fdopen(fd,'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(name,target)
    finally:
        if os.path.exists(name): os.unlink(name)
    return target

def identity(data):
    if not isinstance(data,bytes) or not data or len(data)>MAX_BYTES: raise ValueError('Image must contain 1 to 8388608 bytes')
    return hashlib.sha256(data).hexdigest()

def image_type(data):
    identity(data)
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return 'png'
    if data.startswith(b'\xff\xd8\xff'): return 'jpg'
    if data.startswith((b'II*\x00',b'MM\x00*')): return 'tiff'
    raise ValueError('Only PNG, JPEG and TIFF images are supported')
