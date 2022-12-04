import sqlite3, json, time, uuid
from pathlib import Path


class Conflict(ValueError):
    pass


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connect() as c:
            c.executescript(
                """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS documents(
             id TEXT PRIMARY KEY, digest TEXT NOT NULL UNIQUE, filename TEXT NOT NULL,
             image_path TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'queued',version INTEGER NOT NULL DEFAULT 1,
             payload TEXT NOT NULL DEFAULT '{}', created REAL NOT NULL);
            """
            )

        Path(path).chmod(0o600)

    def connect(self):
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        return c

    def decode(self, row):
        if row is None:
            raise KeyError("Document not found")
        result = dict(row)
        result["payload"] = json.loads(result["payload"])
        return result

    def create(self, digest, filename, image_path):
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid content digest")
        filename = Path(filename).name[:200]
        if not filename:
            raise ValueError("Filename is required")
        with self.connect() as c:
            c.execute(
                "INSERT OR IGNORE INTO documents(id,digest,filename,image_path,created) VALUES(?,?,?,?,?)",
                (uuid.uuid4().hex, digest, filename, str(image_path), time.time()),
            )
            return self.decode(
                c.execute(
                    "SELECT * FROM documents WHERE digest=?", (digest,)
                ).fetchone()
            )

    def cancel(self, identifier, version):
        with self.connect() as c:
            cursor = c.execute(
                "UPDATE documents SET status='rejected',version=version+1 WHERE id=? AND version=? AND status IN ('queued','processing','failed')",
                (identifier, version),
            )
            if cursor.rowcount != 1:
                raise Conflict("Document is no longer cancellable")
        return self.get(identifier)

    def fail(self, identifier, version, error, max_attempts=3):
        if not 1 <= max_attempts <= 10:
            raise ValueError("Invalid retry budget")
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            job = c.execute(
                "SELECT * FROM jobs WHERE document_id=?", (identifier,)
            ).fetchone()
            status = "failed" if job and job["attempts"] >= max_attempts else "queued"
            cursor = c.execute(
                "UPDATE documents SET status=?,version=version+1 WHERE id=? AND version=?",
                (status, identifier, version),
            )
            if cursor.rowcount != 1:
                raise Conflict("Worker lease is stale")
            c.execute(
                "UPDATE jobs SET error=? WHERE document_id=?",
                (str(error)[:200], identifier),
            )
        return self.get(identifier)

    def lease(self, identifier):
        with self.connect() as c:
            row = c.execute(
                "SELECT * FROM jobs WHERE document_id=?", (identifier,)
            ).fetchone()
            return dict(row) if row else None

    def claim(self, worker, now=None, lease_seconds=60):
        if not worker or not 1 <= lease_seconds <= 3600:
            raise ValueError("Invalid worker lease")
        now = time.time() if now is None else now
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            c.execute(
                "CREATE TABLE IF NOT EXISTS jobs(document_id TEXT PRIMARY KEY,worker TEXT,expires REAL,attempts INTEGER DEFAULT 0,error TEXT)"
            )
            c.execute(
                "UPDATE documents SET status='failed',version=version+1 WHERE status='processing' AND id IN (SELECT document_id FROM jobs WHERE expires<=? AND attempts>=3)",
                (now,),
            )
            row = c.execute(
                "SELECT d.* FROM documents d LEFT JOIN jobs j ON j.document_id=d.id WHERE d.status='queued' OR (d.status='processing' AND j.expires<=?) ORDER BY d.created,d.id LIMIT 1",
                (now,),
            ).fetchone()
            if row is None:
                return None
            c.execute(
                "UPDATE documents SET status='processing',version=version+1 WHERE id=?",
                (row["id"],),
            )
            c.execute(
                "INSERT INTO jobs(document_id,worker,expires,attempts) VALUES(?,?,?,1) ON CONFLICT(document_id) DO UPDATE SET worker=excluded.worker,expires=excluded.expires,attempts=jobs.attempts+1",
                (row["id"], worker, now + lease_seconds),
            )
            return self.decode(
                c.execute("SELECT * FROM documents WHERE id=?", (row["id"],)).fetchone()
            )

    def review(self, identifier, version, fields, label, reviewer, action, family=None):
        from .review import validate_corrections

        import re

        if family is not None and (
            not isinstance(family, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", family)
        ):
            raise ValueError("Family must be a stable vendor/template identifier")
        corrections = validate_corrections(fields, label)
        if type(version) is not int or version < 1:
            raise ValueError("Version must be a positive integer")
        if (
            not isinstance(reviewer, str)
            or not 1 <= len(reviewer.strip()) <= 80
            or action not in ("save", "approve", "reject")
        ):
            raise ValueError("Reviewer and action required")
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            row = self.decode(
                c.execute(
                    "SELECT * FROM documents WHERE id=?", (identifier,)
                ).fetchone()
            )
            if row["version"] != version or row["status"] not in (
                "review",
                "approved",
                "rejected",
            ):
                raise Conflict("Document changed; reload before saving")
            payload = row["payload"]
            payload.setdefault("fields", {})
            for name, value in corrections.items():
                previous = payload["fields"].get(name, {})
                payload["fields"][name] = {
                    **previous,
                    "source_value": previous.get("source_value", previous.get("value")),
                    "value": value,
                    "confidence": 1.0,
                    "method": "human-review",
                    "reviewer": reviewer,
                }
            from .extraction import field_issues

            payload["issues"] = field_issues(payload["fields"])
            if action == "approve" and payload["issues"]:
                raise ValueError(
                    "Resolve field issues before approval: "
                    + ", ".join(payload["issues"])
                )
            payload["label"] = label
            if family is not None:
                payload["family"] = family
            status = {"save": "review", "approve": "approved", "reject": "rejected"}[
                action
            ]
            c.execute(
                "UPDATE documents SET payload=?,status=?,version=version+1 WHERE id=?",
                (json.dumps(payload), status, identifier),
            )
            c.execute(
                "CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,document_id TEXT,version INTEGER,reviewer TEXT,action TEXT,changes TEXT,created REAL)"
            )
            c.execute(
                "INSERT INTO events(document_id,version,reviewer,action,changes,created) VALUES(?,?,?,?,?,?)",
                (
                    identifier,
                    version + 1,
                    reviewer,
                    action,
                    json.dumps(
                        {
                            "fields": corrections,
                            "label": label,
                            "family": payload.get("family"),
                        }
                    ),
                    time.time(),
                ),
            )
        return self.get(identifier)

    def events(self, identifier):
        with self.connect() as c:
            exists = c.execute(
                "SELECT 1 FROM sqlite_master WHERE name='events'"
            ).fetchone()
            return (
                [
                    dict(r)
                    for r in c.execute(
                        "SELECT * FROM events WHERE document_id=? ORDER BY id",
                        (identifier,),
                    )
                ]
                if exists
                else []
            )

    def search(self, query, limit=50):
        if (
            not isinstance(query, str)
            or len(query) > 200
            or type(limit) is not int
            or not 1 <= limit <= 200
        ):
            raise ValueError("Invalid search")
        with self.connect() as c:
            return [
                self.decode(r)
                for r in c.execute(
                    "SELECT * FROM documents WHERE instr(lower(filename),lower(?))>0 ORDER BY created,id LIMIT ?",
                    (query, limit),
                )
            ]

    def summary(self):
        result = dict.fromkeys(
            ("queued", "processing", "review", "approved", "rejected", "failed"), 0
        )
        with self.connect() as c:
            result.update(
                {
                    r[0]: r[1]
                    for r in c.execute(
                        "SELECT status,COUNT(*) FROM documents GROUP BY status"
                    )
                }
            )
        return result

    def result(self, identifier, version, payload):
        encoded = json.dumps(payload, allow_nan=False)
        with self.connect() as c:
            cursor = c.execute(
                "UPDATE documents SET payload=?,status='review',version=version+1 WHERE id=? AND version=? AND status IN ('queued','processing','failed')",
                (encoded, identifier, version),
            )
            if cursor.rowcount != 1:
                raise Conflict("Document changed; reload before saving")
        return self.get(identifier)

    def list(self, status=None, limit=50, offset=0):
        if (
            type(limit) is not int
            or not 1 <= limit <= 200
            or type(offset) is not int
            or offset < 0
        ):
            raise ValueError("Invalid pagination")
        if status not in (
            None,
            "queued",
            "processing",
            "review",
            "approved",
            "rejected",
            "failed",
        ):
            raise ValueError("Invalid status")
        with self.connect() as c:
            query = "SELECT * FROM documents"
            args = []
            if status:
                query += " WHERE status=?"
                args.append(status)
            query += " ORDER BY created,id LIMIT ? OFFSET ?"
            args.extend((limit, offset))
            return [self.decode(r) for r in c.execute(query, args)]

    def get(self, identifier):
        with self.connect() as c:
            return self.decode(
                c.execute(
                    "SELECT * FROM documents WHERE id=?", (identifier,)
                ).fetchone()
            )
