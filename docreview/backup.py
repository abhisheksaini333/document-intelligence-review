import sqlite3, json, shutil, hashlib, os
from pathlib import Path


def restore(source, target):
    source = Path(source).resolve()
    target = Path(target).resolve()
    if target.exists():
        raise ValueError("Restore target must not exist")
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest.get("format") != 1 or "review.sqlite" not in manifest.get("files", {}):
        raise ValueError("Unsupported backup format")
    paths = list(source.rglob("*"))
    if any(p.is_symlink() for p in paths):
        raise ValueError("Backup symlinks are forbidden")
    actual = {
        p.relative_to(source).as_posix()
        for p in paths
        if p.is_file() and p.name != "manifest.json"
    }
    if actual != set(manifest["files"]):
        raise ValueError("Backup file inventory mismatch")
    for name, digest in manifest["files"].items():
        path = (source / name).resolve()
        if (
            not path.is_relative_to(source)
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            raise ValueError("Backup integrity failure")
    with sqlite3.connect(
        (source / "review.sqlite").as_uri() + "?mode=ro", uri=True
    ) as c:
        if c.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Backup database is corrupt")
        documents = c.execute("SELECT id,image_path,digest FROM documents").fetchall()
        for identifier, image_path, digest in documents:
            image = source / "images" / Path(image_path).name
            if (
                not image.is_file()
                or hashlib.sha256(image.read_bytes()).hexdigest() != digest
            ):
                raise ValueError("Backup document image is missing or corrupt")
    target.mkdir(parents=True, mode=0o700)
    try:
        shutil.copytree(source, target, dirs_exist_ok=True)
        with sqlite3.connect(target / "review.sqlite") as c:
            for identifier, image_path, digest in documents:
                c.execute(
                    "UPDATE documents SET image_path=? WHERE id=?",
                    (str(target / "images" / Path(image_path).name), identifier),
                )
        return target
    except Exception:
        shutil.rmtree(target)
        raise


def snapshot(source, target):
    source = Path(source).resolve()
    target = Path(target).resolve()
    if target.exists() or target.is_relative_to(source):
        raise ValueError("Backup target must be new and outside the data directory")
    target.mkdir(parents=True, mode=0o700)
    with sqlite3.connect(source / "review.sqlite") as src, sqlite3.connect(
        target / "review.sqlite"
    ) as dst:
        src.backup(dst)
    images = source / "images"
    if images.exists():
        if any(p.is_symlink() for p in images.rglob("*")):
            raise ValueError("Image symlinks are forbidden")
        shutil.copytree(images, target / "images", dirs_exist_ok=True)
    else:
        (target / "images").mkdir()
    files = {
        p.relative_to(target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in target.rglob("*")
        if p.is_file()
    }
    (target / "manifest.json").write_text(
        json.dumps({"format": 1, "files": files}, indent=2)
    )
    for path in target.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
    return target
