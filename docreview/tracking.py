from pathlib import Path
from .benchmark import baseline_benchmark


def track_comparison(report, tracking):
    import mlflow, tempfile, json
    from mlflow.tracking import MlflowClient

    uri = Path(tracking).resolve().as_uri()
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment("document-model-comparison")
    with mlflow.start_run() as run:
        mlflow.log_param("dataset_sha256", report["dataset_sha256"])
        mlflow.log_metrics(
            {
                name + "_macro_f1": result["raw"]["classification"]["macro_f1"]
                for name, result in report["models"].items()
            }
        )
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "comparison.json"
            path.write_text(json.dumps(report, indent=2))
            mlflow.log_artifact(str(path))
        run_id = run.info.run_id
    return {
        "run_id": run_id,
        "metrics": MlflowClient(tracking_uri=uri).get_run(run_id).data.metrics,
    }


def restore_run(tracking, run_id):
    from mlflow.tracking import MlflowClient
    from .baseline import load

    client = MlflowClient(tracking_uri=Path(tracking).resolve().as_uri())
    path = client.download_artifacts(run_id, "evaluation/baseline")
    return load(path)


def track_baseline(directory, tracking):
    import mlflow
    from mlflow.tracking import MlflowClient

    report = baseline_benchmark(directory)
    uri = Path(tracking).resolve().as_uri()
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment("document-classification")
    with mlflow.start_run() as run:
        mlflow.log_params(
            {
                "dataset_sha256": report["dataset_sha256"],
                "split": "family-isolated",
                "classifier": "tfidf-logistic",
                "seed": 17,
            }
        )
        mlflow.log_metrics(
            {k: v for k, v in report["test"].items() if isinstance(v, (int, float))}
        )
        mlflow.log_artifacts(str(directory), "evaluation")
        run_id = run.info.run_id
    client = MlflowClient(tracking_uri=uri)
    record = client.get_run(run_id)
    return {
        "run_id": run_id,
        "metrics": record.data.metrics,
        "artifacts": [a.path for a in client.list_artifacts(run_id, "evaluation")],
    }
