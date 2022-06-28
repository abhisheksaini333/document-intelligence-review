import math

def field_accuracy(expected,extracted):
    if not expected or len(expected)!=len(extracted): raise ValueError('Aligned field records required')
    fields={}
    for truth,found in zip(expected,extracted):
      for name,value in truth.items():
        cell=fields.setdefault(name,{'correct':0,'count':0});cell['count']+=1
        cell['correct']+=int(found.get(name,{}).get('value')==value)
    count=sum(v['count'] for v in fields.values())
    return {'accuracy':sum(v['correct'] for v in fields.values())/count if count else 0,'fields':fields,'count':count}

def classification(actual,predicted):
    if not actual or len(actual)!=len(predicted): raise ValueError('Aligned nonempty labels required')
    labels=sorted(set(actual)|set(predicted));matrix=[[0 for _ in labels] for _ in labels]
    for a,p in zip(actual,predicted): matrix[labels.index(a)][labels.index(p)]+=1
    f1=[]
    for i in range(len(labels)):
        tp=matrix[i][i];fp=sum(row[i] for row in matrix)-tp;fn=sum(matrix[i])-tp
        f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return {'count':len(actual),'accuracy':sum(a==p for a,p in zip(actual,predicted))/len(actual),'macro_f1':sum(f1)/len(f1),'labels':labels,'confusion':matrix}
