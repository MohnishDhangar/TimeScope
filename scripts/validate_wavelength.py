"""Evaluate wavelength prioritization on preserved genuine showcase FITS offline."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
from backend.spectral import ranked_pairs,metrics


def evaluate(folder):
    m=json.loads((folder/'manifest.json').read_text());frames=[];arrays=[]
    ref=WCS(fits.Header(m['reference_wcs']))
    size=max(16,int(np.ceil(m['query']['fov']*60/6.15)))
    for old in m['frames']:
        frame=old.copy();original=folder/(Path(frame['image']).stem+'.fits')
        if hashlib.sha256(original.read_bytes()).hexdigest()!=frame['sha256']:raise ValueError('Original checksum mismatch')
        with fits.open(original) as h:
            head=h['IMAGE'].header
            spatial=WCS(head,h).celestial
            x,y=spatial.world_to_pixel_values(m['query']['ra'],m['query']['dec'])
            spectral_head=head.copy()
            for key in list(spectral_head):
                if key.startswith(('A_','B_','AP_','BP_')):del spectral_head[key]
            wave=WCS(spectral_head,h,key='W').all_pix2world([[x,y]],0)[0]
            frame.update(wavelength_um_at_center=float(wave[0]),bandwidth_um_at_center=float(wave[1]),pipeline_version=h[0].header.get('VERSION'))
            science=h['IMAGE'].data.astype(float)
            science[(h['FLAGS'].data.astype(np.int64)&~((1<<21)|(1<<12)))!=0]=np.nan
            aligned,foot=reproject_interp((science,spatial),ref,shape_out=(size,size));aligned[foot<=0]=np.nan
            arrays.append(aligned);frames.append(frame)
    overlaps={(a,b):float((np.isfinite(arrays[a])&np.isfinite(arrays[b])).mean()) for a in range(len(frames)) for b in range(a+1,len(frames))}
    recommendations=ranked_pairs(frames,overlaps)
    before={'a':0,'b':len(frames)-1,**metrics(frames[0],frames[-1]),'common_coverage':overlaps[(0,len(frames)-1)]}
    after=recommendations[0] if recommendations else None
    for pair in [before,after]:
        if pair is not None:pair['identities']=[frames[pair[key]]['collection']+'/'+frames[pair[key]]['obs_id']+'/'+str(frames[pair[key]]['detector']) for key in ['a','b']]
    return m,frames,{'session_id':m['id'],'field':m.get('label'),'query':m['query'],'candidate_count':len(frames),'before_temporal_endpoints':before,'after_recommended':after,'source_hashes_verified':True,'interpretation':'Offline comparison within preserved candidate pool; approximate visualization WCS only; no quantitative validation.'},recommendations

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folders',nargs='+',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--annotate-bundles',type=Path)
    args=parser.parse_args();reports=[]
    for folder in args.folders:
        m,frames,report,pairs=evaluate(folder)
        reports.append(report)
        if args.annotate_bundles:
            bundle=args.annotate_bundles/m['id']/'manifest.json'
            original=json.loads(bundle.read_text())
            # Only attach measurements for the exact source observations/hashes.
            for target,source in zip(original['frames'],frames):
                if target['sha256']!=source['sha256'] or target['obs_id']!=source['obs_id']:raise ValueError('Bundle mismatch')
                for key in ['bandwidth_um_at_center','pipeline_version']:target[key]=source[key]
            original['selection']={'mode':'temporal','candidate_attempts':len(frames),'processed_candidates':len(frames),'selected_frames':len(frames),'method':'Existing chronological showcase; recommendation evaluated from preserved original FITS using the bounded-pool heuristic.','recommendations':pairs[:5],'limitations':'Approximate visualization WCS-WAVE; response/PSF matching and quantitative comparison are not validated.'}
            bundle.write_text(json.dumps(original,indent=2,allow_nan=False))
    args.output.write_text(json.dumps(reports,indent=2,allow_nan=False));print(json.dumps(reports,indent=2))
