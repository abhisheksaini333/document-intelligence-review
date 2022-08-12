from pathlib import Path
from .store import Store
from .ingest import save_image,identity,validate_image
from .ocr import recognize
from .extraction import extract,field_issues,lines
class Pipeline:
    def __init__(self,directory,model=None):
        self.directory=Path(directory);self.store=Store(self.directory/'review.sqlite');self.model=model
    def ingest(self,data,filename):
        validate_image(data);path=save_image(self.directory/'images',data)
        return self.store.create(identity(data),filename,path)
    def process(self,identifier,expected_version=None):
        from .store import Conflict
        row=self.store.get(identifier)
        if expected_version is not None and row['version']!=expected_version:raise Conflict('Worker lease is stale')
        if row['status'] not in ('queued','processing','failed'): raise Conflict('Reviewed documents cannot be reprocessed')
        tokens=recognize(row['image_path']);fields=extract(tokens);text='\n'.join(line['text'] for line in lines(tokens));prediction=None
        if self.model is not None:
            from .baseline import predict
            prediction=predict(self.model,[text])[0]
        payload={'text':text,'tokens':[t.to_dict() for t in tokens],'fields':fields,'issues':field_issues(fields),'prediction':prediction,'pages':sorted({t.page for t in tokens})}
        from .review import route
        payload['routing']=route(payload)
        return self.store.result(identifier,row['version'],payload)
