import io
import pytest
from astropy.table import Table
from backend.discovery import direct_sia
from backend.pipeline import Search
from backend import discovery


def response(monkeypatch,payload,seen):
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def raise_for_status(self):pass
        def iter_content(self,size):yield payload
    def get(url,**kwargs):seen.update(url=url,**kwargs);return Response()
    monkeypatch.setattr(discovery.requests,'get',get)


def test_direct_query_preserves_field_and_collections(monkeypatch):
    table=Table(rows=[('a','spherex_dr1',1.,'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/a.fits')],names=['obs_id','obs_collection','t_min','access_url'])
    output=io.BytesIO();table.write(output,format='votable')
    payload=output.getvalue().replace(b'ID="obs_id"',b'ID="col_9"')
    seen={};response(monkeypatch,payload,seen)
    result=direct_sia(Search(ra=359.99,dec=-80,fov=6))
    params=seen['params']
    assert next(v for k,v in params if k=='POS').startswith('CIRCLE 359.99 -80.0 ')
    assert [v for k,v in params if k=='COLLECTION']==['spherex_qr3','spherex_dr1']
    assert ('MAXREC','1000') in params
    assert seen['headers']=={'Cache-Control':'no-cache'}
    assert result.meta['discovery_method']=='direct-sia-v2'
    assert len(result)==1


def test_service_error_is_not_an_empty_valid_search(monkeypatch):
    response(monkeypatch,b'<VOTABLE><RESOURCE><INFO name="QUERY_STATUS" value="ERROR">failure</INFO></RESOURCE></VOTABLE>',{})
    with pytest.raises(ValueError,match='query error'):direct_sia(Search(ra=10,dec=20))


def test_missing_columns_rejected(monkeypatch):
    out=io.BytesIO();Table({'x':[1]}).write(out,format='votable')
    response(monkeypatch,out.getvalue(),{})
    with pytest.raises(ValueError,match='metadata'):direct_sia(Search(ra=10,dec=20))


def test_transient_failure_retried_once_without_changing_query(monkeypatch):
    import requests
    table=Table({'obs_id':['a'],'obs_collection':['spherex_dr1'],'t_min':[1.], 'access_url':['https://irsa.ipac.caltech.edu/a']})
    out=io.BytesIO();table.write(out,format='votable')
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def raise_for_status(self):pass
        def iter_content(self,size):yield out.getvalue()
    calls=[]
    def get(url,**kwargs):
        calls.append(kwargs)
        if len(calls)==1:
            r=requests.Response();r.status_code=502
            raise requests.HTTPError(response=r)
        return Response()
    monkeypatch.setattr(discovery.requests,'get',get)
    monkeypatch.setattr(discovery.time,'sleep',lambda seconds:None)
    assert len(direct_sia(Search(ra=10,dec=20)))==1
    assert len(calls)==2 and calls[0]==calls[1]


def test_persistent_discovery_failure_is_bounded(monkeypatch):
    import requests
    calls=[]
    def fail(*args,**kwargs):calls.append(1);raise requests.Timeout('synthetic timeout')
    monkeypatch.setattr(discovery.requests,'get',fail)
    monkeypatch.setattr(discovery.time,'sleep',lambda seconds:None)
    with pytest.raises(requests.Timeout):direct_sia(Search(ra=10,dec=20))
    assert len(calls)==2
