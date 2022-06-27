import argparse, json
from . import __version__
from .fixtures import records

def main():
    parser=argparse.ArgumentParser(description='OCR evidence and review workstation')
    parser.add_argument('--version',action='version',version=__version__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('fixtures',help='Print labeled synthetic documents')
    demo=sub.add_parser('demo',help='Render and process a synthetic invoice');demo.add_argument('--data',default='data')
    args=parser.parse_args()
    if args.command=='demo':
        from pathlib import Path
        from .fixtures import render
        from .pipeline import Pipeline
        path=render(records()[0],Path(args.data)/'demo.png');pipeline=Pipeline(args.data);row=pipeline.ingest(path.read_bytes(),path.name)
        print(json.dumps(pipeline.process(row['id']),indent=2))
    if args.command=='fixtures': print(json.dumps(records(),indent=2))
