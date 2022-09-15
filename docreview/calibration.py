import math

def choose_threshold(actual,predictions,max_risk=.05):
    from .metrics import coverage_curve
    if not 0<=max_risk<=1:raise ValueError('Invalid risk budget')
    thresholds=sorted({0.,1.}|{p['confidence'] for p in predictions})
    candidates=[row for row in coverage_curve(actual,predictions,thresholds) if row['risk'] is not None and row['risk']<=max_risk]
    return max(candidates,key=lambda r:(r['coverage'],-r['threshold'])) if candidates else {'threshold':1.,'coverage':0.,'accepted':0,'risk':None,'abstain_all':True}

def temperature_scale(probabilities,temperature):
    if not math.isfinite(temperature) or temperature<=0:raise ValueError('Invalid temperature')
    if not probabilities or any(not math.isfinite(p) or not 0<=p<=1 for p in probabilities.values()) or abs(sum(probabilities.values())-1)>1e-6:raise ValueError('Invalid probabilities')
    logits={k:math.log(max(v,1e-12))/temperature for k,v in probabilities.items()};maximum=max(logits.values());weights={k:math.exp(v-maximum) for k,v in logits.items()};total=sum(weights.values());return {k:v/total for k,v in weights.items()}

def choose_temperature(actual,probabilities,candidates=(.5,.75,1.,1.5,2.,3.,5.)):
    if not actual or len(actual)!=len(probabilities):raise ValueError('Aligned calibration labels required')
    scores=[]
    for temperature in candidates:
        nll=-sum(math.log(max(temperature_scale(p,temperature).get(label,0),1e-12)) for label,p in zip(actual,probabilities))/len(actual)
        scores.append({'temperature':temperature,'nll':nll})
    return min(scores,key=lambda r:(r['nll'],abs(r['temperature']-1)))
