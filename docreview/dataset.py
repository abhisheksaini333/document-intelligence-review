import hashlib,json

def fingerprint(rows):
    canonical=json.dumps(sorted(rows,key=lambda x:x['id']),sort_keys=True,separators=(',',':'),ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()

def audit_split(parts):
    ids={};families={};texts={}
    for name,rows in parts.items():
      if not rows: raise ValueError('Empty dataset split')
      for row in rows:
        for mapping,key in ((ids,row['id']),(families,row['family']),(texts,' '.join(row['text'].lower().split()))):
            if key in mapping and mapping[key]!=name: raise ValueError('Dataset leakage across '+mapping[key]+' and '+name)
            mapping[key]=name
    return True

def split(rows):
    groups={}
    for row in rows: groups.setdefault(row['label'],set()).add(row['family'])
    mapping={}
    for label,families in sorted(groups.items()):
        ordered=sorted(families)
        if len(ordered)<5: raise ValueError('Each class requires five independent families')
        for family in ordered[:-2]: mapping[family]='train'
        mapping[ordered[-2]]='calibration';mapping[ordered[-1]]='test'
    result={key:[] for key in ('train','calibration','test')}
    for row in rows: result[mapping[row['family']]].append(row)
    return result
