import json,hashlib
from pathlib import Path

def save(model,directory,metadata):
    import joblib
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);target=directory/'model.joblib';joblib.dump(model,target)
    manifest={'format':1,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'metadata':metadata,'classes':list(model.classes_)}
    (directory/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2));return manifest

def load(directory):
    import joblib
    directory=Path(directory);manifest=json.loads((directory/'manifest.json').read_text());target=directory/'model.joblib'
    if manifest.get('format')!=1 or hashlib.sha256(target.read_bytes()).hexdigest()!=manifest['sha256']: raise ValueError('Model artifact failed integrity verification')
    return joblib.load(target)

def train(rows):
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    if len({r['label'] for r in rows})<2: raise ValueError('Training requires at least two classes')
    model=Pipeline([('vectorizer',TfidfVectorizer(ngram_range=(1,2),min_df=1,sublinear_tf=True)),('classifier',LogisticRegression(C=4,max_iter=300,random_state=17))])
    model.fit([r['text'] for r in rows],[r['label'] for r in rows]);return model

def predict(model,texts):
    if not texts or len(texts)>128 or any(not isinstance(t,str) or not t.strip() or len(t)>100000 for t in texts): raise ValueError('Supply 1 to 128 nonempty bounded texts')
    matrix=model.predict_proba(texts)
    return [{'label':str(model.classes_[int(row.argmax())]),'confidence':float(row.max()),'probabilities':{str(k):float(v) for k,v in zip(model.classes_,row)}} for row in matrix]
