import argparse, json
from . import __version__
from .fixtures import records

def main():
    parser=argparse.ArgumentParser(description='OCR evidence and review workstation')
    parser.add_argument('--version',action='version',version=__version__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('fixtures',help='Print labeled synthetic documents')
    args=parser.parse_args()
    if args.command=='fixtures': print(json.dumps(records(),indent=2))
