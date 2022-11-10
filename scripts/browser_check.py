"""Run browser journeys against isolated local review data and owned processes."""
import json, os, signal, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from docreview.fixtures import records, render
from docreview.pipeline import Pipeline

root = Path(__file__).resolve().parents[1]
api_port = int(os.environ.get("CHECK_API_PORT", "4820"))
web_port = int(os.environ.get("CHECK_WEB_PORT", "4821"))
processes = []
try:
    with tempfile.TemporaryDirectory(prefix="folio-browser-") as d:
        directory = Path(d)
        pipeline = Pipeline(directory)
        for index, name in [(0, "demo.png"), (1, "second.png")]:
            image = render(records()[index], directory / name)
            row = pipeline.ingest(image.read_bytes(), name)
            pipeline.process(row["id"])
        report = root / "docs/evaluation.json"
        if report.exists():
            (directory / "evaluation.json").write_bytes(report.read_bytes())
        env = {
            **os.environ,
            "API_TARGET": f"http://127.0.0.1:{api_port}",
            "APP_URL": f"http://127.0.0.1:{web_port}",
        }
        processes.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "docreview",
                    "serve",
                    "--data",
                    d,
                    "--port",
                    str(api_port),
                ],
                cwd=root,
                env=env,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
            )
        )
        processes.append(
            subprocess.Popen(
                [
                    "node",
                    str(root / "frontend/node_modules/vite/bin/vite.js"),
                    str(root / "frontend"),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(web_port),
                    "--strictPort",
                ],
                cwd=root / "frontend",
                env=env,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
            )
        )
        for port, path in [(api_port, "/api/health"), (web_port, "/")]:
            deadline = time.monotonic() + 30
            while True:
                try:
                    with urllib.request.urlopen(
                        urllib.request.Request(
                            f"http://127.0.0.1:{port}{path}",
                            headers={"Accept": "text/html"},
                        ),
                        timeout=1,
                    ) as r:
                        if r.status == 200:
                            break
                except Exception:
                    if time.monotonic() > deadline:
                        raise RuntimeError(
                            f"Browser dependency on {port} did not start"
                        )
                    time.sleep(0.2)
        subprocess.run(
            ["npm", "run", "test:e2e"], cwd=root / "frontend", env=env, check=True
        )
finally:
    for process in reversed(processes):
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
