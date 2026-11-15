import numpy as np
from backend.diagnostics import peaks, match_peaks, compare

def starfield(dx=0,dy=0):
    y,x=np.indices((80,80));data=np.random.default_rng(1).normal(10,.05,(80,80))
    for cx,cy in [(15,15),(35,17),(60,25),(20,55),(55,60)]:
        data+=30*np.exp(-((x-cx-dx)**2+(y-cy-dy)**2)/2)
    return data

def test_recovers_known_subpixel_shift():
    result=compare(starfield(),starfield(.3,-.2),6.12)
    assert result['matched_peaks']==5
    assert abs(result['median_dx_pixels']-.3)<.04
    assert abs(result['median_dy_pixels']+.2)<.04

def test_no_sources_is_not_a_pass():
    assert compare(np.zeros((20,20)),np.zeros((20,20)),6)['status']=='insufficient_matches'
    assert peaks(np.full((20,20),np.nan)).shape==(0,2)

def test_rejects_mask_contaminated_centroid():
    a=starfield();a[14,14]=np.nan
    assert len(peaks(a))==4

def test_one_to_one_matches_and_large_offset_rejected():
    a=np.array([[0,0],[.1,0]])
    assert len(match_peaks(a,np.array([[0,0]])))==1
    assert len(match_peaks(a,np.array([[10,10]])))==0
