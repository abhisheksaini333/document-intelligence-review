import sqlite3,json,shutil,hashlib,os
from pathlib import Path

def restore(source,target):
    source=Path(source).resolve();target=Path(target).resolve()
    if target.exists():raise ValueError('Restore target must not exist')
    manifest=json.loads((source/'manifest.json').read_text())
    if manifest.get('format')!=1:raise ValueError('Unsupported backup format')
    for name,digest in manifest['files'].items():
        path=(source/name).resolve()
        if not path.is_relative_to(source) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Backup integrity failure')
    shutil.copytree(source,target)
    with sqlite3.connect(target/'review.sqlite') as c:
        if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Backup database is corrupt')
        for identifier,path in c.execute('SELECT id,image_path FROM documents').fetchall():
            c.execute('UPDATE documents SET image_path=? WHERE id=?',(str(target/'images'/Path(path).name),identifier))
    return target

def snapshot(source,target):
    source=Path(source).resolve();target=Path(target).resolve()
    if target.exists() or target.is_relative_to(source):raise ValueError('Backup target must be new and outside the data directory')
    target.mkdir(parents=True,mode=0o700)
    with sqlite3.connect(source/'review.sqlite') as src,sqlite3.connect(target/'review.sqlite') as dst:src.backup(dst)
    shutil.copytree(source/'images',target/'images',dirs_exist_ok=True)
    files={p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in target.rglob('*') if p.is_file()}
    (target/'manifest.json').write_text(json.dumps({'format':1,'files':files},indent=2))
    for path in target.rglob('*'):
        if path.is_file():path.chmod(0o600)
    return target
