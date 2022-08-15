from pathlib import Path
from .benchmark import baseline_benchmark

def track_baseline(directory,tracking):
    import mlflow
    from mlflow.tracking import MlflowClient
    report=baseline_benchmark(directory);uri=Path(tracking).resolve().as_uri();mlflow.set_tracking_uri(uri);mlflow.set_experiment('document-classification')
    with mlflow.start_run() as run:
        mlflow.log_params({'dataset_sha256':report['dataset_sha256'],'split':'family-isolated','classifier':'tfidf-logistic','seed':17})
        mlflow.log_metrics({k:v for k,v in report['test'].items() if isinstance(v,(int,float))})
        mlflow.log_artifacts(str(directory),'evaluation')
        run_id=run.info.run_id
    client=MlflowClient(tracking_uri=uri);record=client.get_run(run_id)
    return {'run_id':run_id,'metrics':record.data.metrics,'artifacts':[a.path for a in client.list_artifacts(run_id,'evaluation')]}
