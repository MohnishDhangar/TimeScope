"""Transparent wavelength-prioritized selection using approximate local WCS.

These metrics rank exploratory comparisons; they never authorize subtraction.
"""
import math
from datetime import datetime, timezone


def positive(value):
    return isinstance(value,(int,float)) and math.isfinite(value) and value>0


def metrics(a,b):
    wa,wb=a.get('wavelength_um_at_center'),b.get('wavelength_um_at_center')
    delta=abs(wa-wb) if positive(wa) and positive(wb) else None
    fractional=delta/((wa+wb)/2) if delta is not None else None
    ba,bb=a.get('bandwidth_um_at_center'),b.get('bandwidth_um_at_center')
    widths=delta/((ba+bb)/2) if delta is not None and positive(ba) and positive(bb) else None
    try:
        dates=[]
        for f in [a,b]:
            date=datetime.fromisoformat(f['date'].replace('Z','+00:00'))
            dates.append(date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date.astimezone(timezone.utc))
        days=abs((dates[1]-dates[0]).total_seconds())/86400
    except (ValueError,KeyError,TypeError):days=None
    return {'time_separation_days':days,'absolute_wavelength_difference_um':delta,
            'fractional_wavelength_difference':fractional,'approximate_bandwidth_separation':widths,
            'spectral_metadata':'Approximate field-center WCS-WAVE values, intended for visualization',
            'quantitative_comparison_allowed':False}


def ranked_pairs(frames,overlaps=None):
    candidates=[]
    for i,a in enumerate(frames):
        for j in range(i+1,len(frames)):
            b=frames[j];m=metrics(a,b)
            if (a.get('obs_id'),a.get('detector'),a.get('collection')) == (b.get('obs_id'),b.get('detector'),b.get('collection')):continue
            if not m['time_separation_days'] or m['fractional_wavelength_difference'] is None:continue
            if a.get('detector')!=b.get('detector') or a.get('collection')!=b.get('collection'):continue
            if not a.get('unit') or a['unit'].replace(' ','')!=(b.get('unit') or '').replace(' ',''):continue
            if a.get('pipeline_version') and b.get('pipeline_version') and a['pipeline_version']!=b['pipeline_version']:continue
            overlap=overlaps.get((i,j)) if overlaps is not None else None
            if overlap is not None and overlap<.1:continue
            candidates.append({'a':i,'b':j,**m,'common_coverage':overlap})
    if not candidates:return []
    # Engineering preference: retain pairs spanning at least 25% of the usable
    # baseline, then minimize fractional spectral separation. Not a physics gate.
    longest=max(p['time_separation_days'] for p in candidates)
    candidates=[p for p in candidates if p['time_separation_days']>=longest*.25]
    candidates.sort(key=lambda p:(p['fractional_wavelength_difference'],-p['time_separation_days'],
                                  -(p['common_coverage'] or 0),frames[p['a']]['obs_id'],frames[p['b']]['obs_id']))
    return candidates


def choose_frames(frames,count,overlaps=None):
    pairs=ranked_pairs(frames,overlaps)
    if not pairs:return None
    best=pairs[0];anchor=frames[best['a']]
    mean=(anchor['wavelength_um_at_center']+frames[best['b']]['wavelength_um_at_center'])/2
    chosen=[best['a'],best['b']]
    rest=[i for i,f in enumerate(frames) if i not in chosen and
          positive(f.get('wavelength_um_at_center')) and (f.get('unit') or '').replace(' ','')==anchor['unit'].replace(' ','') and
          f.get('collection')==anchor.get('collection') and f.get('detector')==anchor.get('detector') and
          (not f.get('pipeline_version') or not anchor.get('pipeline_version') or f['pipeline_version']==anchor['pipeline_version'])]
    rest.sort(key=lambda i:(abs(frames[i]['wavelength_um_at_center']-mean)/mean,frames[i]['date'],frames[i]['obs_id']))
    return chosen+rest[:max(0,count-2)]


METHOD='Prefer pairs spanning at least 25% of the longest eligible time baseline; minimize fractional center-wavelength separation, then prefer longer time separation and common coverage. Remaining frames are nearest wavelength neighbors in the same detector/release/units context. Candidate pool is bounded; this is a heuristic, not validated spectral matching.'
