import re, unicodedata
from decimal import Decimal, InvalidOperation
from datetime import datetime

def document_date(value):
    for fmt in ('%Y-%m-%d','%d %b %Y','%d %B %Y'):
        try: return datetime.strptime(value.strip(),fmt).date().isoformat()
        except ValueError: pass
    raise ValueError('Use ISO or a spelled month to avoid ambiguous dates')

def amount(value):
    value=normalize_text(value).strip()
    negative=value.startswith('(') and value.endswith(')')
    if negative: value=value[1:-1]
    value=re.sub(r'^(?:USD|EUR|GBP|[$€£])\s*','',value)
    if not re.fullmatch(r'-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d{1,2})?',value):
        raise ValueError('Invalid decimal amount')
    result=Decimal(value.replace(',',''))
    if negative: result=-result
    return format(result.quantize(Decimal('.01')),'f')

def normalize_text(text):
    text=unicodedata.normalize('NFKC',text).replace('\r\n','\n').replace('\r','\n')
    text=''.join(c for c in text if c in '\n\t' or not unicodedata.category(c).startswith('C'))
    return '\n'.join(re.sub(r'[^\S\n]+',' ',line).strip() for line in text.splitlines()).strip()
