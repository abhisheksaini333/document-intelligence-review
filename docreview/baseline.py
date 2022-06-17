import json,hashlib
from pathlib import Path

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
