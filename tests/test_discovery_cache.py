"""Synthetic inventory metadata tests; no archive traffic."""
from datetime import datetime,timezone,timedelta
import json
import hashlib
import pytest
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
    assert loaded.meta['inventory_kind']=='bundled-historical'
    assert c.load(Search(ra=134.4,dec=-8.5,fov=10),tmp_path) is None
    assert c.load(Search(ra=query.ra,dec=-2.24514722,fov=5),tmp_path) is None


@pytest.mark.parametrize('kind',['runtime-cache','bundled-historical'])
def test_inventory_age_policy_and_immutable_provenance(tmp_path,monkeypatch,kind):
    """Synthetic metadata and mocked clock; no archive requests."""
    query=Search(ra=10,dec=20)
    retrieved=datetime(2026,11,15,12,28,44,tzinfo=timezone.utc)
    bundle=tmp_path/'bundles';bundle.mkdir()
    monkeypatch.setattr(c,'SNAPSHOTS',bundle)
    folder=tmp_path/'discovery-cache' if kind=='runtime-cache' else bundle
    folder.mkdir(exist_ok=True)
    path=folder/f'{c.query_key(query)}.json'
    content=json.dumps(c.record(query,table(),retrieved.isoformat())).encode()
    path.write_bytes(content)
    monkeypatch.setattr(c.time,'time',lambda:retrieved.timestamp()+3600)
    loaded=c.load(query,tmp_path)
    assert loaded.meta['inventory_kind']==kind
    assert loaded.meta['inventory_retrieved_utc']==retrieved.isoformat()
    assert loaded.meta['inventory_snapshot_sha256']==hashlib.sha256(content).hexdigest()
    monkeypatch.setattr(c.time,'time',lambda:retrieved.timestamp()+24*3600+1)
    assert (c.load(query,tmp_path) is None)==(kind=='runtime-cache')
    monkeypatch.setattr(c.time,'time',lambda:retrieved.timestamp()+60*86400)
    loaded=c.load(query,tmp_path)
    if kind=='bundled-historical':
        assert loaded.meta['inventory_retrieved_utc']==retrieved.isoformat()
        assert loaded.meta['inventory_snapshot_sha256']==hashlib.sha256(content).hexdigest()
    else:assert loaded is None
    assert path.read_bytes()==content


@pytest.mark.parametrize('corruption',['schema','url','timestamp','naive','future','nonfinite','collection','row-shape'])
@pytest.mark.parametrize('kind',['runtime-cache','bundled-historical'])
def test_malformed_inventory_rejected(tmp_path,monkeypatch,corruption,kind):
    query=Search(ra=10,dec=20)
    bundle=tmp_path/'bundles';bundle.mkdir()
    monkeypatch.setattr(c,'SNAPSHOTS',bundle)
    instant=datetime(2026,11,15,12,28,44,tzinfo=timezone.utc)
    monkeypatch.setattr(c.time,'time',lambda:instant.timestamp()+10)
    data=c.record(query,table(),instant.isoformat())
    if corruption=='schema':data['schema_version']=True
    if corruption=='url':data['rows'][0][3]='https://example.com/ibe/data/spherex/a.fits'
    if corruption=='timestamp':data['retrieved_utc']='not a timestamp'
    if corruption=='naive':data['retrieved_utc']='2026-11-15T12:28:44'
    if corruption=='future':data['retrieved_utc']=(instant+timedelta(days=1)).isoformat()
    if corruption=='nonfinite':data['rows'][0][2]=float('nan')
    if corruption=='collection':data['rows'][0][1]='unrelated'
    if corruption=='row-shape':data['rows'][0].pop()
    folder=tmp_path/'discovery-cache' if kind=='runtime-cache' else bundle
    folder.mkdir(exist_ok=True)
    (folder/f'{c.query_key(query)}.json').write_text(json.dumps(data))
    assert c.load(query,tmp_path) is None
