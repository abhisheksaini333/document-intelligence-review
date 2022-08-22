from .baseline import load,predict

def classify_request(registry,body):
    if not isinstance(body,dict) or not isinstance(body.get('texts'),list) or not 1<=len(body['texts'])<=128:raise ValueError('texts must contain 1 to 128 strings')
    return registry.classify(body['texts'])

def export_bento(directory):
    import bentoml
    import bentoml.sklearn
    model=load(directory)
    artifact=bentoml.sklearn.save_model('document_classifier',model,signatures={'predict_proba':{'batchable':False}},metadata={'task':'document-type','classes':list(model.classes_)})
    restored=bentoml.sklearn.load_model(artifact.tag)
    return {'tag':str(artifact.tag),'parity':predict(model,['invoice payment due'])==predict(restored,['invoice payment due'])}
