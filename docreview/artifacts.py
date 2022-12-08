import hashlib, json
from pathlib import Path


def seal(directory):
    directory = Path(directory)
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError("Model artifacts cannot contain symlinks")
        if path.is_file() and path.name != "artifact-manifest.json":
            files[path.relative_to(directory).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    if not files:
        raise ValueError("Empty model artifact")
    (directory / "artifact-manifest.json").write_text(
        json.dumps({"format": 1, "files": files}, indent=2)
    )
    return files


def verify(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "artifact-manifest.json").read_text())
    if manifest.get("format") != 1 or not manifest["files"]:
        raise ValueError("Invalid artifact manifest")
    paths = list(directory.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Model artifacts cannot contain symlinks")
    actual = {
        path.relative_to(directory).as_posix()
        for path in paths
        if path.is_file() and path.name != "artifact-manifest.json"
    }
    if actual != set(manifest["files"]):
        raise ValueError("Model artifact inventory mismatch")
    for name, digest in manifest["files"].items():
        path = (directory / name).resolve()
        if (
            not path.is_relative_to(directory.resolve())
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            raise ValueError("Model artifact integrity failure")
    return True
