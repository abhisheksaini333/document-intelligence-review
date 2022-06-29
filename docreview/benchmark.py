import json
from pathlib import Path
from .fixtures import records
from .dataset import split,audit_split,fingerprint
from .baseline import train,predict,save,load
from .metrics import classification

def baseline_benchmark(directory):
    rows=records();parts=split(rows);audit_split(parts);model=train(parts['train']);directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    output=predict(model,[r['text'] for r in parts['test']]);digest=fingerprint(rows)
    save(model,directory/'baseline',{'dataset_sha256':digest,'train_ids':[r['id'] for r in parts['train']]})
    report={'scope':'Synthetic English invoice, purchase-order and receipt templates; not real-world accuracy','dataset_sha256':digest,'split_sizes':{k:len(v) for k,v in parts.items()},'test':classification([r['label'] for r in parts['test']],[p['label'] for p in output]),'reload_equal':output==predict(load(directory/'baseline'),[r['text'] for r in parts['test']])}
    (directory/'baseline-report.json').write_text(json.dumps(report,indent=2));return report
