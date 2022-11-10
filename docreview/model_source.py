"""Acquire content-pinned model files without executing downloaded code."""
import hashlib, json, os, tempfile, urllib.request
from pathlib import Path


def fetch_source(manifest, directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    for name, metadata in manifest["files"].items():
        target = (directory / name).resolve()
        if not target.is_relative_to(directory) or target == directory:
            raise ValueError("Unsafe model filename")
        if (
            target.exists()
            and hashlib.sha256(target.read_bytes()).hexdigest() == metadata["sha256"]
        ):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".model-", dir=target.parent)
        try:
            with urllib.request.urlopen(
                metadata["url"], timeout=60
            ) as response, os.fdopen(fd, "wb") as output:
                total = 0
                digest = hashlib.sha256()
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > 512 * 1024 * 1024:
                        raise ValueError("Model file exceeds download limit")
                    output.write(chunk)
                    digest.update(chunk)
            if digest.hexdigest() != metadata["sha256"]:
                raise ValueError("Downloaded model checksum mismatch")
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    (directory / "source-manifest.json").write_text(json.dumps(manifest, indent=2))
    return directory
