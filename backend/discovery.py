"""Bounded direct SIA discovery, independent of the capabilities endpoint."""
import io
import math
import time
import xml.etree.ElementTree as ET
import requests
from astropy.table import Table


def direct_sia(search):
    # Equivalent to Astroquery's query. This ordering + cache revalidation was
    # observed succeeding while the prior URL returned 502. Cause unconfirmed.
    params=[('MAXREC','1000'),('COLLECTION','spherex_qr3'),('COLLECTION','spherex_dr1'),
            ('POS',f'CIRCLE {search.ra} {search.dec} {search.fov/120*math.sqrt(2)}')]
    for attempt in range(2):
        try:
            with requests.get('https://irsa.ipac.caltech.edu/SIA',params=params,
                              headers={'Cache-Control':'no-cache'},
                              timeout=(10,35),stream=True) as response:
                response.raise_for_status()
                chunks=[];size=0
                for chunk in response.iter_content(65536):
                    size+=len(chunk)
                    if size>16*1024*1024:raise ValueError('Discovery response exceeds 16 MiB')
                    chunks.append(chunk)
            break
        except requests.RequestException as exc:
            status=exc.response.status_code if exc.response is not None else None
            if attempt or (status is not None and status not in (429,502,503,504)):
                raise
            time.sleep(2)
    payload=b''.join(chunks)
    infos=[e for e in ET.fromstring(payload).iter() if e.tag.split('}')[-1]=='INFO' and e.get('name')=='QUERY_STATUS']
    if any(e.get('value')=='ERROR' for e in infos):raise ValueError('SIA returned a query error')
    table=Table.read(io.BytesIO(payload),format='votable',use_names_over_ids=True)
    if not {'obs_id','obs_collection','t_min','access_url'}.issubset(table.colnames):
        raise ValueError('SIA returned incomplete observation metadata')
    table.meta['discovery_method']='direct-sia-v2'
    table.meta['discovery_transport']='GET with cache revalidation; at most two attempts'
    table.meta['query_overflow']=any(e.get('value')=='OVERFLOW' for e in infos)
    return table
