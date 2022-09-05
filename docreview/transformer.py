import hashlib,json,random
from pathlib import Path

SOURCE_REPOSITORY='distilbert/distilbert-base-uncased'
SOURCE_REVISION='043235d6088ecd3dd5fb5ca3592b6913fd516027'

from dataclasses import dataclass,asdict
import math
@dataclass(frozen=True)
class TrainingConfig:
    epochs:int=3
    batch_size:int=4
    max_length:int=128
    learning_rate:float=3e-5
    seed:int=17
    threads:int=2
    def __post_init__(self):
        if not 1<=self.epochs<=20 or not 1<=self.batch_size<=32 or not 16<=self.max_length<=512 or not math.isfinite(self.learning_rate) or not 0<self.learning_rate<=.01 or not 1<=self.threads<=4:raise ValueError('Invalid training budget')

def verify_source(directory):
    directory=Path(directory);manifest=json.loads((directory/'source-manifest.json').read_text())
    if len(manifest['revision'])!=40 or not manifest['files']:raise ValueError('Invalid source manifest')
    for filename,metadata in manifest['files'].items():
        path=(directory/filename).resolve()
        if not path.is_relative_to(directory.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=metadata['sha256']:raise ValueError('Transformer source checksum mismatch')
    return manifest
