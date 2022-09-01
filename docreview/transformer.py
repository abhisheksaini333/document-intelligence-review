import hashlib,json,random
from pathlib import Path

SOURCE_REPOSITORY='distilbert/distilbert-base-uncased'
SOURCE_REVISION='043235d6088ecd3dd5fb5ca3592b6913fd516027'

def verify_source(directory):
    directory=Path(directory);manifest=json.loads((directory/'source-manifest.json').read_text())
    if len(manifest['revision'])!=40 or not manifest['files']:raise ValueError('Invalid source manifest')
    for filename,metadata in manifest['files'].items():
        path=(directory/filename).resolve()
        if not path.is_relative_to(directory.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=metadata['sha256']:raise ValueError('Transformer source checksum mismatch')
    return manifest
