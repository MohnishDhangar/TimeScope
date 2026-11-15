"""Synthetic metadata selection controls. No fabricated NASA measurements."""
from backend.spectral import metrics,ranked_pairs,choose_frames
from backend.pipeline import Search,selection
from astropy.table import Table
import pytest


def frame(i,date,wave,**kw):
    return dict(obs_id=str(i),date=date,wavelength_um_at_center=wave,bandwidth_um_at_center=.03,
                detector=2,collection='spherex_dr1',unit='MJy/sr',**kw)


def test_prioritizes_similar_wavelength_over_near_identical_time():
    frames=[frame(0,'2025-01-01',1.2),frame(1,'2025-01-02',1.20001),frame(2,'2025-07-01',1.201),frame(3,'2025-12-01',1.5)]
    ranked=ranked_pairs(frames)
    assert (ranked[0]['a'],ranked[0]['b'])==(1,2)
    assert set(choose_frames(frames,2))=={1,2}
    assert ranked==ranked_pairs(frames)


def test_unknown_wavelength_cannot_be_a_matched_pair():
    assert not ranked_pairs([frame(0,'2025-01-01',None),frame(1,'2025-05-01',1.2)])
    assert choose_frames([frame(0,'2025-01-01',1.2)],2) is None


def test_unknown_bandwidth_keeps_fractional_metric_but_no_resolution_claim():
    a,b=frame(0,'2025-01-01',1.2),frame(1,'2025-05-01',1.21)
    a.pop('bandwidth_um_at_center')
    m=metrics(a,b)
    assert m['fractional_wavelength_difference']>0
    assert m['approximate_bandwidth_separation'] is None
    assert not m['quantitative_comparison_allowed']


def test_same_time_context_mismatch_or_no_overlap_is_rejected():
    a,b=frame(0,'2025-01-01',1.2),frame(1,'2025-01-01',1.2)
    assert not ranked_pairs([a,b])
    b['date']='2025-07-01'
    assert not ranked_pairs([a,b],{(0,1):.01})
    b['unit']='Jy/sr';assert not ranked_pairs([a,b])
    b['unit']='MJy/sr';b['detector']=3;assert not ranked_pairs([a,b])
    b['detector']=2;b['collection']='spherex_qr3';assert not ranked_pairs([a,b])


def test_deterministic_ties():
    frames=[frame(0,'2025-01-01',1.2),frame(1,'2025-07-01',1.2),frame(2,'2026-01-01',1.2)]
    assert ranked_pairs(frames)[0]['time_separation_days']==365
    assert set(choose_frames(frames,2))=={0,2}


def test_detector_constraint_preserves_release_deduplication_and_temporal_mode():
    rows=[]
    for detector in [1,2]:
        for i in [0,1,2]:
            for collection in ['qr3','dr1']:
                rows.append((str(i),'spherex_'+collection,float(i),f'https://irsa.ipac.caltech.edu/ibe/data/spherex/{collection}/{detector}/{i}.fits'))
    table=Table(rows=rows,names=['obs_id','obs_collection','t_min','access_url'])
    temporal=selection(table,2)
    assert [r['obs_id'] for r in temporal]==['0','2']
    chosen=selection(table[::-1],2,detector=2)
    assert all('/2/' in r['access_url'] and r['obs_collection']=='spherex_dr1' for r in chosen)
    assert [r['access_url'] for r in chosen]==[r['access_url'] for r in selection(table,2,detector=2)]
    with pytest.raises(ValueError):selection(table,2,detector=6)


@pytest.mark.parametrize('fields',[{'detector':0},{'detector':7},{'selection_mode':'unknown'}])
def test_invalid_selection_settings_rejected(fields):
    with pytest.raises(ValueError):Search(ra=10,dec=20,**fields)


def test_session_identity_includes_selection_and_detector():
    base=Search(ra=10,dec=20).model_dump()
    assert base!=Search(ra=10,dec=20,detector=2).model_dump()
    assert base!=Search(ra=10,dec=20,selection_mode='wavelength_matched').model_dump()


def test_missing_unit_duplicate_identity_and_timezone_offsets():
    a=frame(0,'2025-01-01T00:00:00Z',1.2)
    b=frame(1,'2025-01-02T01:00:00+01:00',1.201)
    assert metrics(a,b)['time_separation_days']==1
    b['unit']=None
    assert not ranked_pairs([a,b])
    b['unit']='MJy/sr';b['obs_id']='0'
    assert not ranked_pairs([a,b])
