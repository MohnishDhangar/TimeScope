"""Synthetic inventory metadata tests; no archive traffic."""
from datetime import datetime,timezone,timedelta
import json
from astropy.table import Table
from backend import discovery_cache as c
from backend.pipeline import Search


def table():
    return Table(rows=[('a','spherex_dr1',60000.,'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/a.fits'),('b','spherex_dr1',60100.,'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/b.fits')],names=['obs_id','obs_collection','t_min','access_url'])


def test_only_exact_region_and_settings_can_reuse_inventory(tmp_path,monkeypatch):
    monkeypatch.setattr(c,'SNAPSHOTS',tmp_path/'none')
    query=Search(ra=10,dec=20,fov=5)
    c.save(query,table(),tmp_path)
    loaded=c.load(query,tmp_path)
    assert loaded is not None and loaded.meta['discovery_cached']
    assert loaded.meta['inventory_retrieved_utc']
    assert c.load(Search(ra=10.1,dec=20,fov=5),tmp_path) is None
    assert c.load(Search(ra=10,dec=21,fov=5),tmp_path) is None
    assert c.load(Search(ra=10,dec=20,fov=6),tmp_path) is None
    # Frame count affects selection, not this unfiltered discovery request.
    assert c.load(Search(ra=10,dec=20,fov=5,frames=2),tmp_path) is not None


def test_old_or_forged_inventory_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(c,'SNAPSHOTS',tmp_path/'none')
    query=Search(ra=10,dec=20)
    c.save(query,table(),tmp_path)
    path=tmp_path/'discovery-cache'/f'{c.query_key(query)}.json'
    data=json.loads(path.read_text())
    data['retrieved_utc']=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat()
    path.write_text(json.dumps(data))
    assert c.load(query,tmp_path) is None
    data['retrieved_utc']=datetime.now(timezone.utc).isoformat()
    data['query']['ra']=12
    path.write_text(json.dumps(data))
    assert c.load(query,tmp_path) is None


def test_subset_never_promoted_to_query_cache(tmp_path):
    rows=table();rows.meta['discovery_limited']=True
    c.save(Search(ra=10,dec=20),rows,tmp_path)
    assert not (tmp_path/'discovery-cache').exists()


def test_original_verified_snapshot_does_not_cover_a_different_field(tmp_path):
    query=Search(ra=133.79512917,dec=-7.24514722,fov=5)
    loaded=c.load(query,tmp_path)
    assert loaded is not None and len(loaded)==289
    assert loaded.meta['discovery_cached']
    assert c.load(Search(ra=134.4,dec=-8.5,fov=10),tmp_path) is None
