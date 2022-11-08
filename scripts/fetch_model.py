#!/usr/bin/env python3
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from docreview.model_source import fetch_source
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'model-sources.json').read_text())
print(fetch_source(manifest,root/'models/upstream/distilbert'))
