import json,re,os,tempfile,shutil,fcntl
from pathlib import Path
from .baseline import save,load,predict

class Registry:
    def __init__(self,directory):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
    def install(self,version,model,metadata):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',version):raise ValueError('Invalid model version')
        target=self.directory/version
        if target.exists():raise ValueError('Model versions are immutable')
        stage=Path(tempfile.mkdtemp(prefix='.install-',dir=self.directory))
        try:save(model,stage,metadata);load(stage);stage.rename(target)
        finally:
            if stage.exists():shutil.rmtree(stage)
        return version
    def versions(self):
        return sorted(p.name for p in self.directory.iterdir() if p.is_dir() and not p.name.startswith('.') and (p/'manifest.json').exists())
