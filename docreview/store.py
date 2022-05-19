import sqlite3, json, time, uuid
from pathlib import Path
class Conflict(ValueError): pass
class Store:
    def __init__(self,path):
        self.path=str(path); Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as c:
            c.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS documents(
             id TEXT PRIMARY KEY, digest TEXT NOT NULL UNIQUE, filename TEXT NOT NULL,
             image_path TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'queued',version INTEGER NOT NULL DEFAULT 1,
             payload TEXT NOT NULL DEFAULT '{}', created REAL NOT NULL);
            """)
    def connect(self):
        c=sqlite3.connect(self.path,timeout=10); c.row_factory=sqlite3.Row
        return c
    def decode(self,row):
        if row is None: raise KeyError('Document not found')
        result=dict(row); result['payload']=json.loads(result['payload']); return result
    def create(self,digest,filename,image_path):
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest): raise ValueError('Invalid content digest')
        filename=Path(filename).name[:200]
        if not filename: raise ValueError('Filename is required')
        with self.connect() as c:
            c.execute('INSERT OR IGNORE INTO documents(id,digest,filename,image_path,created) VALUES(?,?,?,?,?)',(uuid.uuid4().hex,digest,filename,str(image_path),time.time()))
            return self.decode(c.execute('SELECT * FROM documents WHERE digest=?',(digest,)).fetchone())
    def get(self,identifier):
        with self.connect() as c: return self.decode(c.execute('SELECT * FROM documents WHERE id=?',(identifier,)).fetchone())
