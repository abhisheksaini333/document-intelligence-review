import argparse, json
from . import __version__
from .fixtures import records


def main():
    parser = argparse.ArgumentParser(description="OCR evidence and review workstation")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fixtures", help="Print labeled synthetic documents")
    demo = sub.add_parser("demo", help="Render and process a synthetic invoice")
    demo.add_argument("--data", default="data")
    serve = sub.add_parser("serve", help="Run the local review API")
    serve.add_argument("--data", default="data")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=4800)
    train = sub.add_parser("train", help="Train and evaluate the fixed baseline")
    train.add_argument("--output", default="artifacts/baseline-run")
    registry = sub.add_parser(
        "registry", help="Install, activate or roll back a verified baseline"
    )
    registry.add_argument(
        "operation", choices=["install", "activate", "rollback", "status"]
    )
    registry.add_argument("--directory", default="data/registry")
    registry.add_argument("--version")
    registry.add_argument("--artifact")
    registry.add_argument("--revision", type=int, default=0)
    worker = sub.add_parser("worker", help="Process leased OCR jobs")
    worker.add_argument("--data", default="data")
    worker.add_argument("--name", default="local-worker")
    worker.add_argument("--once", action="store_true")
    benchmark = sub.add_parser(
        "benchmark", help="Compare baseline and DistilBERT on grouped holdouts"
    )
    benchmark.add_argument("--source", default="models/upstream/distilbert")
    benchmark.add_argument("--output", default="artifacts/comparison")
    benchmark.add_argument("--epochs", type=int, default=3)
    feedback = sub.add_parser(
        "feedback", help="Export approved labels or select uncertain examples"
    )
    feedback.add_argument("--data", default="data")
    feedback.add_argument("--select", action="store_true")
    feedback.add_argument("--limit", type=int, default=20)
    backup = sub.add_parser(
        "backup", help="Create or restore a verified review snapshot"
    )
    backup.add_argument("operation", choices=["snapshot", "restore"])
    backup.add_argument("source")
    backup.add_argument("target")
    feedback_train = sub.add_parser(
        "feedback-train",
        help="Retrain reviewed labels with explicitly assigned families",
    )
    feedback_train.add_argument("input")
    feedback_train.add_argument("--output", default="artifacts/feedback")
    args = parser.parse_args()
    if args.command == "feedback-train":
        from pathlib import Path
        from .feedback import retrain_feedback

        print(
            json.dumps(
                retrain_feedback(json.loads(Path(args.input).read_text()), args.output),
                indent=2,
            )
        )
    if args.command == "feedback":
        from .pipeline import Pipeline
        from .feedback import export_corrections, select_examples

        store = Pipeline(args.data).store
        if args.select:
            rows = [
                {
                    "id": r["id"],
                    "digest": r["digest"],
                    "probabilities": r["payload"]["prediction"]["probabilities"],
                }
                for r in store.list(status="review", limit=200)
                if r["payload"].get("prediction")
            ]
            result = select_examples(rows, args.limit)
        else:
            result = export_corrections(store)
        print(json.dumps(result, indent=2))
    if args.command == "backup":
        from .backup import snapshot, restore

        print(
            (snapshot if args.operation == "snapshot" else restore)(
                args.source, args.target
            )
        )
    if args.command == "benchmark":
        from .comparison import compare

        print(json.dumps(compare(args.source, args.output, args.epochs), indent=2))
    if args.command == "worker":
        import time
        from .pipeline import Pipeline
        from .worker import once

        pipeline = Pipeline(args.data)
        while True:
            result = once(pipeline, args.name)
            if args.once:
                print(json.dumps(result))
                break
            if result is None:
                time.sleep(1)
    if args.command == "train":
        from .benchmark import baseline_benchmark

        print(json.dumps(baseline_benchmark(args.output), indent=2))
    if args.command == "registry":
        from .registry import Registry
        from .baseline import load

        registry = Registry(args.directory)
        if args.operation == "install":
            result = registry.install(
                args.version, load(args.artifact), {"artifact": args.artifact}
            )
        elif args.operation == "activate":
            result = registry.activate(args.version, args.revision)
        elif args.operation == "rollback":
            result = registry.rollback(args.revision)
        else:
            result = {"active": registry.active(), "versions": registry.versions()}
        print(json.dumps(result, indent=2))
    if args.command == "serve":
        import os
        from .api import create_server

        server = create_server(
            args.data, args.host, args.port, os.environ.get("REVIEW_TOKEN")
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    if args.command == "demo":
        from pathlib import Path
        from .fixtures import render
        from .pipeline import Pipeline

        path = render(records()[0], Path(args.data) / "demo.png")
        pipeline = Pipeline(args.data)
        row = pipeline.ingest(path.read_bytes(), path.name)
        print(json.dumps(pipeline.process(row["id"]), indent=2))
    if args.command == "fixtures":
        print(json.dumps(records(), indent=2))
