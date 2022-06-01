import csv,io,subprocess
from pathlib import Path
from .domain import Token,Box
from .normalize import normalize_text

def parse_tsv(text):
    reader=csv.DictReader(io.StringIO(text),delimiter='\t')
    required={'level','page_num','left','top','width','height','conf','text'}
    if not required.issubset(reader.fieldnames or []): raise ValueError('Invalid Tesseract TSV header')
    result=[]
    for row in reader:
        if row['level']!='5' or not row['text'].strip(): continue
        confidence=float(row['conf'])
        if confidence<0: continue
        result.append(Token(normalize_text(row['text']),confidence,Box(*(int(row[k]) for k in ('left','top','width','height'))),int(row['page_num'])))
    return result
