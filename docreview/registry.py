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
    def active(self):
        path=self.directory/'active.json'
        return json.loads(path.read_text()) if path.exists() else {'revision':0,'version':None,'previous':None}
    def activate(self,version,expected_revision):
        if version not in self.versions():raise ValueError('Unknown model version')
        load(self.directory/version)
        with (self.directory/'.registry.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);current=self.active()
            if current['revision']!=expected_revision:raise ValueError('Registry changed; reload active revision')
            next_state={'version':version,'previous':current['version'],'revision':current['revision']+1}
            fd,name=tempfile.mkstemp(prefix='.active-',dir=self.directory)
            with os.fdopen(fd,'w') as f:json.dump(next_state,f);f.flush();os.fsync(f.fileno())
            os.replace(name,self.directory/'active.json');return next_state
    def versions(self):
        return sorted(p.name for p in self.directory.iterdir() if p.is_dir() and not p.name.startswith('.') and (p/'manifest.json').exists())
