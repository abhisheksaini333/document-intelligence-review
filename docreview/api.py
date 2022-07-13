import json,base64,threading,os
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
from pathlib import Path
from .pipeline import Pipeline
from .store import Conflict

def create_server(directory,host='127.0.0.1',port=4800,token=None):
    pipeline=Pipeline(directory)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def respond(self,status,data):
            body=json.dumps(data,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            try:
                path=urlsplit(self.path).path;params=parse_qs(urlsplit(self.path).query)
                if path=='/api/health': return self.respond(200,{'status':'ok'})
                if path=='/api/summary': return self.respond(200,pipeline.store.summary())
                if path=='/api/documents': return self.respond(200,pipeline.store.list(status=params.get('status',[None])[0],limit=int(params.get('limit',['50'])[0]),offset=int(params.get('offset',['0'])[0])))
                if path.startswith('/api/documents/'): return self.respond(200,pipeline.store.get(path.split('/')[3]))
                self.respond(404,{'error':'Not found'})
            except KeyError: self.respond(404,{'error':'Document not found'})
            except ValueError as exc: self.respond(400,{'error':str(exc)})
    server=ThreadingHTTPServer((host,port),Handler);server.pipeline=pipeline;return server
