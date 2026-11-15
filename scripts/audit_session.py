"""Reconstruct aligned arrays from preserved FITS; attach exploratory diagnostics."""
import sys, json, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
from PIL import Image
from backend.diagnostics import compare
from backend.pipeline import DATA

def audit(folder):
    path=folder/'manifest.json'
    m=json.loads(path.read_text()); ref=WCS(fits.Header(m['reference_wcs']))
    arrays=[]
    for f in m['frames']:
        name=Path(f['image']).stem
        original=folder/f'{name}.fits'
        if hashlib.sha256(original.read_bytes()).hexdigest()!=f['sha256']:
            raise ValueError('Original FITS checksum mismatch')
        with fits.open(original) as h:
            science=h['IMAGE'].data.astype(float)
            science[(h['FLAGS'].data.astype(np.int64)&~((1<<21)|(1<<12)))!=0]=np.nan
            size=Image.open(folder/f'{name}.png').size[0]
            arr,foot=reproject_interp((science,WCS(h['IMAGE'].header,h).celestial),ref,shape_out=(size,size))
            arr[foot<=0]=np.nan;arrays.append(arr)
            # Remove spatial SIP before constructing the alternate wavelength WCS.
            header=h['IMAGE'].header.copy()
            for key in list(header):
                if key.startswith(('A_','B_','AP_','BP_')): del header[key]
            spectral=WCS(header,h,key='W')
            y,x=np.indices(science.shape)
            values=spectral.all_pix2world(np.column_stack([x.ravel(),y.ravel()]),0)
            wave=values[:,0].reshape(science.shape)
            band=values[:,1].reshape(science.shape)
            finite=np.isfinite(science)&np.isfinite(wave)&np.isfinite(band)&(band>0)
            f['wavelength_range_um']=[float(wave[finite].min()),float(wave[finite].max())] if finite.any() else None
            f['median_bandwidth_um']=float(np.median(band[finite])) if finite.any() else None
    reports=[]
    for i in range(len(arrays)):
        for j in range(i+1,len(arrays)):
            report=compare(arrays[i],arrays[j],abs(ref.wcs.cdelt[0])*3600)
            report.update(a=i,b=j)
            report['quantitative_comparison_allowed']=False
            reports.append(report)
    m['diagnostics']={'method':'bright-peak-centroids-v1','pairs':reports,
       'limitations':'Exploratory geometry only; wavelength responses and PSFs are not matched. No quantitative subtraction is enabled.'}
    m['warnings']=[w.replace('Source-based registration residuals are not yet measured.','Catalog-confirmed stationary-source residuals are not yet measured.') for w in m['warnings']]
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(m,indent=2,allow_nan=False));tmp.replace(path)
    return m
if __name__=='__main__':
    m=audit(DATA/sys.argv[1])
    for p in m['diagnostics']['pairs']:
        print(p['a'],p['b'],p['matched_peaks'],p['status'],p['median_separation_pixels'])
