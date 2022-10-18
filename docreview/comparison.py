import json,time
from pathlib import Path
from .metrics import classification,calibration,coverage_curve
from .calibration import choose_temperature,temperature_scale,choose_threshold
from .dataset import split,audit_split,fingerprint
from .fixtures import records
from .baseline import train,predict,save
from .transformer import train_transformer,TransformerClassifier,TrainingConfig

def finalize_comparison(report):
    report['promotion']=promotion_decision(report['models']['baseline']['calibrated'],report['models']['transformer']['calibrated'])
    return report

def promotion_decision(baseline,candidate,min_gain=.01,max_ece_regression=.02):
    gain=candidate['classification']['macro_f1']-baseline['classification']['macro_f1'];ece_delta=candidate['calibration']['ece']-baseline['calibration']['ece']
    reasons=[]
    if gain<min_gain:reasons.append('insufficient_f1_gain')
    if ece_delta>max_ece_regression:reasons.append('calibration_regression')
    return {'promote':not reasons,'f1_gain':gain,'ece_delta':ece_delta,'reasons':reasons}

def evaluate_predictions(rows,predictions):
    labels=[r['label'] for r in rows]
    return {'classification':classification(labels,[p['label'] for p in predictions]),'calibration':calibration(labels,[p['probabilities'] for p in predictions]),'coverage':coverage_curve(labels,predictions)}

def compare(source,output,epochs=3):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);rows=records();parts=split(rows);audit_split(parts);baseline=train(parts['train']);save(baseline,output/'baseline',{'dataset_sha256':fingerprint(rows)})
    training=train_transformer(parts['train'],source,output/'transformer',TrainingConfig(epochs=epochs));transformer=TransformerClassifier(output/'transformer')
    report={'scope':'180 synthetic English documents, 15 layout families; results do not estimate real-world document accuracy','dataset_sha256':fingerprint(rows),'split_ids':{k:[r['id'] for r in v] for k,v in parts.items()},'split_families':{k:sorted({r['family'] for r in v}) for k,v in parts.items()},'training':training,'models':{}}
    for name,fn in [('baseline',lambda texts:predict(baseline,texts)),('transformer',transformer.predict)]:
        calibration_raw=fn([r['text'] for r in parts['calibration']]);temperature=choose_temperature([r['label'] for r in parts['calibration']],[p['probabilities'] for p in calibration_raw])
        def calibrated(predictions):
            result=[]
            for p in predictions:
                probs=temperature_scale(p['probabilities'],temperature['temperature']);label=max(probs,key=probs.get);result.append({'label':label,'confidence':probs[label],'probabilities':probs})
            return result
        calibrated_validation=calibrated(calibration_raw);threshold=choose_threshold([r['label'] for r in parts['calibration']],calibrated_validation)
        started=time.monotonic();raw=fn([r['text'] for r in parts['test']]);elapsed=time.monotonic()-started
        report['models'][name]={'raw':evaluate_predictions(parts['test'],raw),'calibrated':evaluate_predictions(parts['test'],calibrated(raw)),'temperature':temperature,'selected_threshold':threshold,'test_seconds':elapsed}
    before=transformer.predict([r['text'] for r in parts['test']]);reloaded=TransformerClassifier(output/'transformer');report['transformer_reload_equal']=before==reloaded.predict([r['text'] for r in parts['test']])
    finalize_comparison(report)
    (output/'comparison.json').write_text(json.dumps(report,indent=2));return report
