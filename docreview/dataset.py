import hashlib,json

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
