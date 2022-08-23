import os
import bentoml
from bentoml.io import JSON
from bentoml.exceptions import BadInput
from docreview.registry import Registry
from docreview.serving import classify_request

svc=bentoml.Service('document_classifier')
registry=Registry(os.environ.get('MODEL_REGISTRY','data/registry'))

@svc.api(input=JSON(),output=JSON())
def classify(body):
    try:return classify_request(registry,body)
    except (ValueError,TypeError,KeyError) as exc:raise BadInput(str(exc)) from exc

@svc.api(input=JSON(),output=JSON())
def model(body):
    return {'active':registry.active(),'versions':registry.versions()}
