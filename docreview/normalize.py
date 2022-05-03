import re, unicodedata
from decimal import Decimal, InvalidOperation
from datetime import datetime

def normalize_text(text):
    text=unicodedata.normalize('NFKC',text).replace('\r\n','\n').replace('\r','\n')
    text=''.join(c for c in text if c in '\n\t' or not unicodedata.category(c).startswith('C'))
    return '\n'.join(re.sub(r'[^\S\n]+',' ',line).strip() for line in text.splitlines()).strip()
