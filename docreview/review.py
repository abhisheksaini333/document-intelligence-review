from .normalize import amount,document_date,normalize_text
from .fixtures import LABELS

def validate_corrections(fields,label):
    if label not in LABELS or not isinstance(fields,dict): raise ValueError('Invalid document class or fields')
    result={}
    for name,value in fields.items():
        if name not in ('number','date','subtotal','tax','total','currency') or not isinstance(value,str) or not 1<=len(value)<=200: raise ValueError('Invalid correction field')
        value=normalize_text(value)
        if name in ('subtotal','tax','total'): value=amount(value)
        if name=='date': value=document_date(value)
        if name=='currency' and value not in ('USD','EUR','GBP'): raise ValueError('Unsupported currency')
        result[name]=value
    return result
