"""Retrieve a bounded real-data sequence at explicit ICRS coordinates."""
import argparse
import json
import sys
import uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.pipeline import run, Search
from backend.errors import PipelineError

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ra', type=float, default=133.79512917)
    parser.add_argument('--dec', type=float, default=-7.24514722)
    parser.add_argument('--fov', type=float, default=5)
    parser.add_argument('--frames', type=int, default=6)
    args = parser.parse_args()
    query = Search(**vars(args))
    identifier = uuid.uuid4().hex
    print(json.dumps({'id':identifier,'query':query.model_dump()}),flush=True)
    try:
        result = run(query,identifier,lambda s:print(s,flush=True))
    except PipelineError as error:
        print(json.dumps({'id':identifier,'status':'failed','reason':str(error)}),flush=True)
        sys.exit(1)
    print(json.dumps({'id':result['id'],'status':'ready','frames':len(result['frames']),'partial':result.get('partial',False)}),flush=True)
