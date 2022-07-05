import math

def export_corrections(store):
    result=[];offset=0
    while True:
        rows=store.list(status='approved',limit=200,offset=offset)
        if not rows: break
        for row in rows:
            payload=row['payload'];result.append({'id':row['id'],'digest':row['digest'],'version':row['version'],'text':payload.get('text',''),'label':payload['label'],'fields':{k:v['value'] for k,v in payload.get('fields',{}).items()},'family':payload.get('family',row['digest']),'source':'human-reviewed'})
        offset+=len(rows)
    return result
