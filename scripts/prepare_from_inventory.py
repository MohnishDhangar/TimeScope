"""Retrieve fresh cutouts from a preserved inventory's convex footprint subset."""
import argparse, hashlib, sys, uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from astropy.table import Table
from backend.pipeline import run, Search


def contains(region,ra,dec):
    words=str(region).split()
    if words[:2]!=['POLYGON','ICRS']:return False
    coords=np.array([float(x) for x in words[2:]]).reshape(-1,2)
    def xyz(values):
        a,d=np.deg2rad(values).T
        return np.column_stack([np.cos(d)*np.cos(a),np.cos(d)*np.sin(a),np.sin(d)])
    vertices=xyz(coords);point=xyz(np.array([[ra,dec]]))[0]
    normals=np.cross(vertices,np.roll(vertices,-1,axis=0))
    normals=normals[np.linalg.norm(normals,axis=1)>1e-12]
    if len(normals)<3:return False
    dots=normals@point
    return bool((np.all(dots>=-1e-12) or np.all(dots<=1e-12)) and np.dot(vertices.mean(axis=0),point)>0)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory',type=Path)
    parser.add_argument('--ra',type=float,required=True);parser.add_argument('--dec',type=float,required=True)
    parser.add_argument('--fov',type=float,default=10);parser.add_argument('--frames',type=int,default=6)
    args=parser.parse_args();query=Search(ra=args.ra,dec=args.dec,fov=args.fov,frames=args.frames)
    rows=Table.read(args.inventory)
    selected=rows[[contains(r['s_region'],query.ra,query.dec) for r in rows]]
    selected.meta.update(discovery_method='saved-inventory-center-footprint-subset',discovery_limited=True,
        inventory_sha256=hashlib.sha256(args.inventory.read_bytes()).hexdigest(),
        inventory_source=args.inventory.parent.name,complete_archive_search=False)
    print('Candidate exposures:',len(selected),'from',len(rows),flush=True)
    identifier=uuid.uuid4().hex;print('Session:',identifier,flush=True)
    result=run(query,identifier,lambda msg:print(msg,flush=True),inventory=selected)
    print('READY',result['id'],len(result['frames']),flush=True)
