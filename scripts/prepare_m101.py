"""Bounded M101 retrieval following IRSA's published TAP cutout tutorial.
This center-point query is not a replacement for the application's FOV query.
"""
import sys, uuid, re, json, io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import requests
from astropy.table import Table
from backend import pipeline as p
query="""SELECT TOP 400 a.uri, p.time_bounds_lower
FROM spherex.artifact a JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', 210.80227, 54.34895), p.poly)
AND p.energy_bandpassname = 'SPHEREx-D2' ORDER BY p.time_bounds_lower"""
if __name__=='__main__':
    response=requests.get('https://irsa.ipac.caltech.edu/TAP/sync',params={'REQUEST':'doQuery','LANG':'ADQL','FORMAT':'votable','QUERY':query},timeout=(10,60))
    response.raise_for_status()
    table=Table.read(io.BytesIO(response.content),format='votable')
    print('TAP rows:',len(table),flush=True)
    rows=[]
    for row in table:
        uri=str(row['uri']);url='https://irsa.ipac.caltech.edu/'+uri.lstrip('/')
        match=re.search(r'/spherex/(dr1|qr3)/.*level2_(.+)D[1-6]_spx',url)
        if match:rows.append((match[2],'spherex_'+match[1],float(row['time_bounds_lower']),url))
    observations=Table(rows=rows,names=['obs_id','obs_collection','t_min','access_url'])
    p.Irsa.query_sia=lambda **kwargs:observations
    identifier=uuid.uuid4().hex
    result=p.run(p.Search(ra=210.80227,dec=54.34895,fov=6,frames=4),identifier,lambda msg:print(msg,flush=True))
    result['discovery_method']='IRSA TAP center-point query, detector D2; TOP 400 ordered by time'
    result['discovery_query']=query
    result['possibly_truncated']=len(table)>=400
    result['warnings'].append('Example discovery uses a center-point TAP query restricted to detector D2; not a complete field-of-view search.')
    (p.DATA/identifier/'manifest.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print('READY',identifier,flush=True)
