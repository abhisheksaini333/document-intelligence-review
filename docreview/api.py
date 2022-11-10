import json, base64, threading, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs
from pathlib import Path
from .pipeline import Pipeline
from .store import Conflict


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("Nonfinite JSON numbers are forbidden")

    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def static_asset(directory, url):
    import mimetypes
    from urllib.parse import unquote

    root = Path(directory).resolve()
    relative = unquote(url).lstrip("/") or "index.html"
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise ValueError("Invalid asset path")
    if not target.is_file():
        raise KeyError("Asset not found")
    return (
        target.read_bytes(),
        mimetypes.guess_type(str(target))[0] or "application/octet-stream",
    )


def create_server(
    directory, host="127.0.0.1", port=4800, token=None, request_timeout=10
):
    pipeline = Pipeline(directory)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, data):
            body = json.dumps(data, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def body(self):
            self.connection.settimeout(request_timeout)
            if self.headers.get("Transfer-Encoding"):
                raise ValueError("Chunked requests are unsupported")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Use application/json")
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 12 * 1024 * 1024:
                raise ValueError("Invalid request size")
            import time

            deadline = time.monotonic() + request_timeout
            chunks = []
            remaining = length
            while remaining:
                budget = deadline - time.monotonic()
                if budget <= 0:
                    raise TimeoutError("Request deadline exceeded")
                self.connection.settimeout(budget)
                part = self.rfile.read1(min(remaining, 65536))
                if not part:
                    break
                chunks.append(part)
                remaining -= len(part)
            raw = b"".join(chunks)
            if len(raw) != length:
                raise ValueError("Incomplete request body")
            body = strict_json(raw)
            if not isinstance(body, dict):
                raise ValueError("JSON object required")
            return body

        def do_POST(self):
            try:
                import hmac

                origin = self.headers.get("Origin")
                if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                    return self.respond(
                        403, {"error": "Cross-origin writes are forbidden"}
                    )
                if token and not hmac.compare_digest(
                    self.headers.get("X-Review-Token", ""), token
                ):
                    return self.respond(401, {"error": "Review access token required"})
                body = self.body()
                path = urlsplit(self.path).path
                if path == "/api/documents":
                    data = base64.b64decode(body["image"], validate=True)
                    return self.respond(201, pipeline.ingest(data, body["filename"]))
                parts = path.strip("/").split("/")
                if len(parts) == 4 and parts[:2] == ["api", "documents"]:
                    if parts[3] == "process":
                        return self.respond(200, pipeline.process(parts[2]))
                    if parts[3] == "review":
                        return self.respond(
                            200,
                            pipeline.store.review(
                                parts[2],
                                body["version"],
                                body["fields"],
                                body["label"],
                                body["reviewer"],
                                body["action"],
                            ),
                        )
                self.respond(404, {"error": "Not found"})
            except Conflict as exc:
                self.respond(409, {"error": str(exc)})
            except (ValueError, KeyError, TypeError) as exc:
                self.respond(400, {"error": str(exc)})
            except TimeoutError:
                self.respond(408, {"error": "Request deadline exceeded"})
            except (OSError, RuntimeError):
                self.respond(
                    503,
                    {
                        "error": "Document processing is unavailable; retry after checking the service"
                    },
                )

        def do_GET(self):
            try:
                path = urlsplit(self.path).path
                params = parse_qs(urlsplit(self.path).query)
                if not path.startswith("/api/"):
                    data, content_type = static_asset(
                        Path(__file__).resolve().parent.parent / "frontend" / "dist",
                        path,
                    )
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                if path == "/api/evaluation":
                    report = pipeline.directory / "evaluation.json"
                    return self.respond(
                        200,
                        json.loads(report.read_text())
                        if report.exists()
                        else {"available": False},
                    )
                if path == "/api/feedback":
                    from .feedback import export_corrections

                    return self.respond(200, export_corrections(pipeline.store))
                if path.startswith("/api/documents/") and path.endswith("/events"):
                    return self.respond(200, pipeline.store.events(path.split("/")[3]))
                if path == "/api/health":
                    return self.respond(200, {"status": "ok"})
                if path == "/api/search":
                    return self.respond(
                        200, pipeline.store.search(params.get("q", [""])[0])
                    )
                if path == "/api/summary":
                    return self.respond(200, pipeline.store.summary())
                if path == "/api/documents":
                    return self.respond(
                        200,
                        pipeline.store.list(
                            status=params.get("status", [None])[0],
                            limit=int(params.get("limit", ["50"])[0]),
                            offset=int(params.get("offset", ["0"])[0]),
                        ),
                    )
                if path.startswith("/api/documents/") and path.endswith("/image"):
                    from .ingest import identity, image_type

                    row = pipeline.store.get(path.split("/")[3])
                    data = Path(row["image_path"]).read_bytes()
                    if identity(data) != row["digest"]:
                        raise ValueError("Image integrity check failed")
                    from .ingest import preview

                    data = preview(data, int(params.get("page", ["1"])[0]))
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                if path.startswith("/api/documents/"):
                    return self.respond(200, pipeline.store.get(path.split("/")[3]))
                self.respond(404, {"error": "Not found"})
            except KeyError:
                self.respond(404, {"error": "Document not found"})
            except ValueError as exc:
                self.respond(400, {"error": str(exc)})

    server = ThreadingHTTPServer((host, port), Handler)
    server.pipeline = pipeline
    return server
