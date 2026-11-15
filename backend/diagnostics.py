"""Exploratory checks, not an astrometric solution or variability classifier."""
import numpy as np
from scipy.ndimage import maximum_filter
from scipy.spatial.distance import cdist
from astropy.stats import sigma_clipped_stats


def peaks(image):
    valid = np.isfinite(image)
    if valid.sum() < 25:
        return np.empty((0, 2))
    _, median, std = sigma_clipped_stats(image[valid], sigma=3)
    threshold = median + max(5*std, np.finfo(float).eps)
    filled = np.where(valid,image,-np.inf)
    ys,xs = np.where((filled == maximum_filter(filled,size=5)) & (filled > threshold))
    found = []
    for y,x in zip(ys,xs):
        if y < 2 or x < 2 or y >= image.shape[0]-2 or x >= image.shape[1]-2:
            continue
        patch = image[y-2:y+3,x-2:x+3]
        if not np.all(np.isfinite(patch)):
            continue
        weights = np.maximum(patch-median,0)
        total = weights.sum()
        if total <= 0: continue
        yy,xx = np.indices(patch.shape)
        found.append([x-2+float((weights*xx).sum()/total),y-2+float((weights*yy).sum()/total)])
    return np.array(found).reshape(-1,2)


def match_peaks(a,b,radius=2.):
    if not len(a) or not len(b): return np.empty((0,2))
    distances = cdist(a,b)
    nearest = distances.argmin(axis=1)
    reverse = distances.argmin(axis=0)
    return np.array([b[j]-a[i] for i,j in enumerate(nearest) if reverse[j]==i and distances[i,j]<=radius]).reshape(-1,2)


def compare(a,b,pixel_arcsec):
    pa,pb = peaks(a),peaks(b)
    offsets = match_peaks(pa,pb)
    result = {'peaks_a':len(pa),'peaks_b':len(pb),'matched_peaks':len(offsets),
      'match_radius_pixels':2.,'overlap_fraction':float((np.isfinite(a)&np.isfinite(b)).mean()),
      'status':'insufficient_matches','median_separation_pixels':None,'median_separation_arcsec':None,
      'note':'Mutual nearest bright-peak matches within 2 pixels; not catalog-confirmed stationary stars. Masking, blending, wavelength and PSF differences can bias results. Large offsets may be missed by the matching radius.'}
    if len(offsets)>=3:
        radial = np.linalg.norm(offsets,axis=1)
        result.update(status='preliminary',median_separation_pixels=float(np.median(radial)),
          median_separation_arcsec=float(np.median(radial)*pixel_arcsec),
          median_dx_pixels=float(np.median(offsets[:,0])),median_dy_pixels=float(np.median(offsets[:,1])))
    return result
