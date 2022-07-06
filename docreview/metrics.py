import math

def coverage_curve(actual,predictions,thresholds=(0,.5,.7,.8,.9,.95,1)):
    if not actual or len(actual)!=len(predictions): raise ValueError('Aligned predictions required')
    result=[]
    for threshold in thresholds:
        if not 0<=threshold<=1: raise ValueError('Invalid confidence threshold')
        selected=[(a,p) for a,p in zip(actual,predictions) if p['confidence']>=threshold]
        result.append({'threshold':threshold,'coverage':len(selected)/len(actual),'accepted':len(selected),'risk':sum(a!=p['label'] for a,p in selected)/len(selected) if selected else None})
    return result

def calibration(actual,probabilities,bins=10):
    if not actual or len(actual)!=len(probabilities) or not 1<=bins<=100: raise ValueError('Aligned probabilities required')
    buckets=[[] for _ in range(bins)];brier=0
    for label,probs in zip(actual,probabilities):
        if label not in probs or any(not math.isfinite(v) or not 0<=v<=1 for v in probs.values()) or abs(sum(probs.values())-1)>1e-6: raise ValueError('Invalid probability distribution')
        predicted=max(probs,key=probs.get);confidence=probs[predicted]
        buckets[min(int(confidence*bins),bins-1)].append((confidence,int(predicted==label)))
        brier+=sum((v-int(k==label))**2 for k,v in probs.items())
    result=[];ece=0
    for i,bucket in enumerate(buckets):
        confidence=sum(x[0] for x in bucket)/len(bucket) if bucket else 0;accuracy=sum(x[1] for x in bucket)/len(bucket) if bucket else 0
        ece+=len(bucket)/len(actual)*abs(confidence-accuracy)
        result.append({'lower':i/bins,'upper':(i+1)/bins,'count':len(bucket),'confidence':confidence,'accuracy':accuracy})
    return {'ece':ece,'brier':brier/len(actual),'bins':result}

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
