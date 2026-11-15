"""One-pass diagnostic, requests + standard library only; no automatic retries.

Local results are not Cloud Run measurements. Responses are saved beside output
for inspection; an HTTP 200 alone is not counted as successful discovery.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import time
import xml.etree.ElementTree as ET

import requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ra', type=float, required=True)
    parser.add_argument('--dec', type=float, required=True)
    parser.add_argument('--fov', type=float, required=True)
    parser.add_argument('--repeats', type=int, default=2, choices=(1, 2))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pos = ('POS', f'CIRCLE {args.ra} {args.dec} {args.fov/120*math.sqrt(2)}')
    both = [('COLLECTION', 'spherex_qr3'), ('COLLECTION', 'spherex_dr1')]
    query = f"""SELECT TOP 100 a.uri, p.time_bounds_lower, p.energy_bandpassname
FROM spherex.artifact a JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {args.ra}, {args.dec}), p.poly)
ORDER BY p.time_bounds_lower"""
    variants = [
        ('sia-baseline', 'SIA', [('MAXREC', '1000'), *both, pos], True),
        ('sia-maxrec100', 'SIA', [('MAXREC', '100'), *both, pos], True),
        ('sia-dr1-only', 'SIA', [('MAXREC', '100'), ('COLLECTION', 'spherex_dr1'), pos], True),
        ('sia-qr3-only', 'SIA', [('MAXREC', '100'), ('COLLECTION', 'spherex_qr3'), pos], True),
        ('sia-no-cache-header', 'SIA', [('MAXREC', '1000'), *both, pos], False),
        ('tap-point', 'TAP/sync', {'REQUEST': 'doQuery', 'LANG': 'ADQL', 'FORMAT': 'csv', 'QUERY': query}, False),
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {'environment': 'local', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'query': {'ra': args.ra, 'dec': args.dec, 'fov_arcmin': args.fov},
              'repeats': args.repeats, 'automatic_retries': 0, 'attempts': []}
    with requests.Session() as session:
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=0))
        for repeat in range(1, args.repeats+1):
            for name, route, params, header in variants:
                item = {'variant': name, 'repeat': repeat, 'utc': datetime.now(timezone.utc).isoformat(),
                        'status': None, 'rows': None, 'votable': False, 'discovery_success': False}
                started = time.monotonic()
                try:
                    with session.get('https://irsa.ipac.caltech.edu/'+route, params=params,
                                     headers={'Cache-Control': 'no-cache'} if header else {},
                                     timeout=(5, 20), stream=True, allow_redirects=False) as response:
                        item.update(status=response.status_code, url=response.url,
                                    content_type=response.headers.get('Content-Type'))
                        chunks = []; size = 0
                        for chunk in response.iter_content(65536):
                            size += len(chunk)
                            if size > 16*1024*1024: raise ValueError('Response exceeds 16 MiB')
                            chunks.append(chunk)
                        payload = b''.join(chunks)
                    item['bytes'] = len(payload)
                    item['sha256'] = hashlib.sha256(payload).hexdigest()
                    file = args.output.parent / f'{args.output.stem}-{name}-{repeat}.response'
                    file.write_bytes(payload)
                    item['response_file'] = file.name
                    if response.status_code == 200:
                        if route == 'TAP/sync':
                            rows = list(csv.reader(io.StringIO(payload.decode())))
                            item['columns'] = rows[0] if rows else []
                            if {'uri', 'time_bounds_lower', 'energy_bandpassname'}.issubset(item['columns']):
                                item.update(rows=max(0, len(rows)-1), discovery_success=True)
                        else:
                            tree = ET.fromstring(payload)
                            item['votable'] = tree.tag.split('}')[-1] == 'VOTABLE'
                            infos = [e.get('value') for e in tree.iter() if e.tag.split('}')[-1] == 'INFO' and e.get('name') == 'QUERY_STATUS']
                            item['query_status'] = infos
                            item['columns'] = [e.get('name') or e.get('ID') for e in tree.iter() if e.tag.split('}')[-1] == 'FIELD']
                            tabledata = [e for e in tree.iter() if e.tag.split('}')[-1] == 'TABLEDATA']
                            if tabledata: item['rows'] = sum(e.tag.split('}')[-1] == 'TR' for e in tabledata[0])
                            item['discovery_success'] = item['votable'] and 'ERROR' not in infos and {'obs_id', 'access_url', 't_min', 'obs_collection'}.issubset(item['columns'])
                except Exception as exc:
                    item.update(exception_class=type(exc).__name__, error=str(exc))
                item['duration_seconds'] = round(time.monotonic()-started, 3)
                report['attempts'].append(item)
                args.output.write_text(json.dumps(report, indent=2)+'\n')
                print(json.dumps({k: item.get(k) for k in ('variant', 'repeat', 'status', 'rows', 'votable', 'discovery_success', 'duration_seconds', 'exception_class')}), flush=True)
                time.sleep(1)
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    args.output.write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
