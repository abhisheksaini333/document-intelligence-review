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
    def summary(self):
        result=dict.fromkeys(('queued','processing','review','approved','rejected','failed'),0)
        with self.connect() as c:
            result.update({r[0]:r[1] for r in c.execute('SELECT status,COUNT(*) FROM documents GROUP BY status')})
        return result
    def result(self,identifier,version,payload):
        encoded=json.dumps(payload,allow_nan=False)
        with self.connect() as c:
            cursor=c.execute("UPDATE documents SET payload=?,status='review',version=version+1 WHERE id=? AND version=?",(encoded,identifier,version))
            if cursor.rowcount!=1: raise Conflict('Document changed; reload before saving')
        return self.get(identifier)
    def list(self,status=None,limit=50,offset=0):
        if type(limit) is not int or not 1<=limit<=200 or type(offset) is not int or offset<0: raise ValueError('Invalid pagination')
        if status not in (None,'queued','processing','review','approved','rejected','failed'): raise ValueError('Invalid status')
        with self.connect() as c:
            query='SELECT * FROM documents'; args=[]
            if status: query+=' WHERE status=?'; args.append(status)
            query+=' ORDER BY created,id LIMIT ? OFFSET ?'; args.extend((limit,offset))
            return [self.decode(r) for r in c.execute(query,args)]
    def get(self,identifier):
        with self.connect() as c: return self.decode(c.execute('SELECT * FROM documents WHERE id=?',(identifier,)).fetchone())
