import csv,io,subprocess
from pathlib import Path
from .domain import Token,Box
from .normalize import normalize_text

def recognize(path,timeout=15,executable='tesseract'):
    from .ingest import validate_image
    if not 0<timeout<=120: raise ValueError('OCR timeout must be between zero and 120 seconds')
    path=Path(path).resolve();validate_image(path.read_bytes())
    try: result=subprocess.run([executable,str(path),'stdout','-l','eng','--psm','6','tsv'],capture_output=True,text=True,timeout=timeout,check=True)
    except subprocess.TimeoutExpired as exc: raise TimeoutError('OCR deadline exceeded') from exc
    except (subprocess.CalledProcessError,OSError) as exc: raise RuntimeError('OCR engine could not process image') from exc
    tokens=parse_tsv(result.stdout)
    if not tokens: raise ValueError('No readable text found')
    return tokens

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
