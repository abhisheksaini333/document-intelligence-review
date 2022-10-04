from .normalize import amount,document_date,normalize_text
from .fixtures import LABELS

def route(payload,threshold=.85,min_ocr=.75):
    if not 0<=threshold<=1 or not 0<=min_ocr<=1: raise ValueError('Invalid routing threshold')
    from .extraction import field_issues
    reasons=list(payload.get('issues',[]))+field_issues(payload.get('fields',{}));prediction=payload.get('prediction')
    if not prediction: reasons.append('unclassified')
    elif prediction['confidence']<threshold: reasons.append('uncertain_class')
    if any(v.get('confidence',0)<min_ocr for v in payload.get('fields',{}).values()): reasons.append('low_ocr_confidence')
    return {'recommendation':'review' if reasons else 'eligible','reasons':sorted(set(reasons))}

def validate_corrections(fields,label):
    if label not in LABELS or not isinstance(fields,dict): raise ValueError('Invalid document class or fields')
    result={}
    for name,value in fields.items():
        if name not in ('number','date','subtotal','tax','total','currency') or not isinstance(value,str) or not 1<=len(value)<=200: raise ValueError('Invalid correction field')
        value=normalize_text(value)
        if not value:raise ValueError('Correction cannot be blank')
        if name in ('subtotal','tax','total'): value=amount(value)
        if name=='date': value=document_date(value)
        if name=='currency' and value not in ('USD','EUR','GBP'): raise ValueError('Unsupported currency')
        result[name]=value
    return result
