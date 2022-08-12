from .store import Conflict

def once(pipeline,worker='local-worker'):
    row=pipeline.store.claim(worker)
    if row is None:return None
    try:return pipeline.process(row['id'],expected_version=row['version'])
    except Conflict:raise
    except (ValueError,RuntimeError,TimeoutError) as exc:return pipeline.store.fail(row['id'],row['version'],str(exc))
