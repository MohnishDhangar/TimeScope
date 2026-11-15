"""Synthetic VO/HTTP failure fixtures. Mock clock, sleep and jitter; no NASA traffic."""
import io
import socket
from email.utils import formatdate
import pytest
import requests
from astropy.table import Table
from backend import discovery as d
from backend.pipeline import Search

QUERY=Search(ra=359.99,dec=-80,fov=6)


def payload(count=2):
    table=Table(rows=[(str(i),'spherex_dr1',60000.+i,
                      f'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/{i}.fits') for i in range(count)],
                names=['obs_id','obs_collection','t_min','access_url'],
                dtype=['U32','U32',float,'U128'])
    output=io.BytesIO();table.write(output,format='votable')
    return output.getvalue()


def response(status=200,body=None,headers=None):
    result=requests.Response()
    result.status_code=status
    result.url=d.SIA_URL
    result._content=payload() if body is None else body
    result._content_consumed=True
    result.raw=io.BytesIO(result._content)
    result.headers.update(headers or {})
    return result


@pytest.fixture
def clock(monkeypatch):
    class Clock:
        now=1000.
        sleeps=[]
        def sleep(self,seconds):
            self.sleeps.append(seconds);self.now+=seconds
    value=Clock()
    monkeypatch.setattr(d.time,'monotonic',lambda:value.now)
    monkeypatch.setattr(d.time,'sleep',value.sleep)
    monkeypatch.setattr(d.random,'uniform',lambda a,b:1.)
    monkeypatch.setenv('TIMESCOPE_DISCOVERY_BUDGET_S','90')
    return value


@pytest.fixture
def wire(monkeypatch):
    calls=[]
    def install(outcomes):
        iterator=iter(outcomes)
        def request(self,method,url,**kwargs):
            calls.append({'method':method,'url':url,**kwargs})
            value=next(iterator)
            if isinstance(value,BaseException):raise value
            if callable(value):value=value()
            return value
        monkeypatch.setattr(requests.Session,'request',request)
        return calls
    return install


def test_first_try_uses_actual_astroquery_client_without_hidden_requests(wire,clock):
    calls=wire([response()])
    result=d.discover(QUERY)
    assert len(result)==2 and result.meta['discovery_attempts']==1
    assert result.meta['discovery_method']=='astroquery-sia-v2'
    assert len(calls)==1 and calls[0]['url']==d.SIA_URL
    assert calls[0]['allow_redirects'] is False
    assert calls[0]['params']['COLLECTION']==['spherex_dr1','spherex_qr3']
    assert not clock.sleeps


def test_direct_query_preserves_field_collections_names_and_cap(wire,clock):
    body=payload().replace(b'ID="obs_id"',b'ID="col_9"')
    calls=wire([response(body=body)])
    result=d.direct_sia(QUERY,deadline=clock.now+90)
    params=calls[0]['params']
    assert next(v for k,v in params if k=='POS').startswith('CIRCLE 359.99 -80.0 ')
    assert [v for k,v in params if k=='COLLECTION']==['spherex_qr3','spherex_dr1']
    assert ('MAXREC','1000') in params
    assert calls[0]['headers']=={'Cache-Control':'no-cache'}
    assert result.meta['discovery_method']=='direct-sia-v2'
    assert 'obs_id' in result.colnames


def test_success_on_attempt_four_and_actual_progress_events(wire,clock,caplog):
    messages=[]
    calls=wire([response(502),response(503),response(504),response()])
    result=d.discover(QUERY,messages.append)
    assert len(calls)==4 and clock.sleeps==[2,4,8]
    assert result.meta['discovery_attempts']==4
    assert result.meta['discovery_method']=='direct-sia-v2'
    assert [f['http_status'] for f in result.meta['discovery_failures']]==[502,503,504]
    assert messages[0]=='Searching SPHEREx DR1 and QR3 observations'
    assert 'IRSA returned HTTP 504. Retrying discovery in 8.0 s (attempt 4 of 6)' in messages
    records=[r for r in caplog.records if 'IRSA discovery attempt' in r.message]
    assert len(records)==3 and all(r.exc_info for r in records)


@pytest.mark.parametrize('status',[502,503,504])
def test_retriable_http_status_classification(status,wire,clock):
    calls=wire([response(status),response()])
    result=d.discover(QUERY)
    assert len(calls)==2
    assert result.meta['discovery_failures'][0]['code']=='archive_http_5xx'
    assert result.meta['discovery_failures'][0]['http_status']==status


def test_exhaustion_is_six_wire_attempts_across_all_routes(wire,clock):
    calls=wire([requests.ReadTimeout('Synthetic read timeout') for _ in range(10)])
    with pytest.raises(d.DiscoveryError) as exc:d.discover(QUERY)
    assert exc.value.code=='archive_timeout' and exc.value.retryable
    assert len(calls)==6 and len(exc.value.attempt_log)==6
    assert clock.sleeps==[2,4,8,16,30]
    assert {a['route'] for a in exc.value.attempt_log}=={'direct SIA','Astroquery SIA (explicit query endpoint)'}


@pytest.mark.parametrize('header',['7','date'])
def test_rate_limit_honors_retry_after_if_it_fits(header,wire,clock,monkeypatch):
    if header=='date':
        monkeypatch.setattr(d.time,'time',lambda:1000000.)
        header=formatdate(1000007,usegmt=True)
    wire([response(429,headers={'Retry-After':header}),response()])
    result=d.discover(QUERY)
    assert clock.sleeps==[7]
    assert result.meta['discovery_failures'][0]['code']=='archive_rate_limited'


def test_retry_after_outside_budget_stops_without_sleep(wire,clock):
    calls=wire([response(429,headers={'Retry-After':'120'})])
    with pytest.raises(d.DiscoveryError) as exc:d.discover(QUERY)
    assert exc.value.code=='archive_rate_limited' and len(calls)==1 and not clock.sleeps


@pytest.mark.parametrize('failure,code',[
    (requests.ConnectTimeout('Synthetic connect timeout'),'archive_timeout'),
    (requests.ReadTimeout('Synthetic read timeout'),'archive_timeout'),
    (requests.ConnectionError(ConnectionResetError(104,'Synthetic connection reset')),'archive_invalid_response'),
    (requests.ConnectionError(socket.gaierror(-2,'Synthetic DNS failure')),'network_unreachable'),
    (requests.ConnectionError(ConnectionRefusedError(111,'Synthetic refusal')),'network_unreachable'),
])
def test_only_supported_transient_transport_failures_retry(failure,code,wire,clock):
    calls=wire([failure,response()])
    result=d.discover(QUERY)
    assert len(calls)==2 and result.meta['discovery_failures'][0]['code']==code


@pytest.mark.parametrize('status',[400,401,403,404,405,422,500])
def test_nonretryable_http_failure_is_not_retried(status,wire,clock):
    calls=wire([response(status)])
    with pytest.raises(d.DiscoveryError) as exc:d.discover(QUERY)
    assert not exc.value.retryable and len(calls)==1 and not clock.sleeps
    assert exc.value.code==('archive_http_5xx' if status==500 else 'archive_query_rejected')


@pytest.mark.parametrize('kind,code',[
    ('invalid','archive_invalid_response'),('html','archive_invalid_response'),
    ('query-error','archive_query_rejected'),('schema','archive_schema_changed'),
    ('url','archive_schema_changed'),('unsupported-collection','archive_schema_changed'),
])
def test_deterministic_vo_errors_never_retry(kind,code,wire,clock):
    if kind=='invalid':body=b'<not complete XML'
    elif kind=='html':body=b'<html>Not a VOTable</html>'
    elif kind=='query-error':body=b'<VOTABLE><RESOURCE><INFO name="QUERY_STATUS" value="ERROR">Synthetic invalid query</INFO></RESOURCE></VOTABLE>'
    elif kind=='schema':
        out=io.BytesIO();Table({'x':[1]}).write(out,format='votable');body=out.getvalue()
    elif kind=='url':body=payload().replace(b'irsa.ipac.caltech.edu',b'example.invalid')
    else:body=payload().replace(b'spherex_dr1',b'unsupported')
    calls=wire([response(body=body)])
    with pytest.raises(d.DiscoveryError) as exc:d.discover(QUERY)
    assert exc.value.code==code and len(calls)==1 and not clock.sleeps


def test_valid_empty_result_is_success_not_an_outage(wire,clock):
    calls=wire([response(body=payload(0))])
    result=d.discover(QUERY)
    assert len(result)==0 and len(calls)==1


def test_budget_checks_requests_and_sleep(wire,clock,monkeypatch):
    monkeypatch.setenv('TIMESCOPE_DISCOVERY_BUDGET_S','9')
    calls=wire([response(502)]*6)
    with pytest.raises(d.DiscoveryError):d.discover(QUERY)
    assert len(calls)==3 and clock.sleeps==[2,4]
    assert clock.now==1006.


def test_processing_reserve_is_preserved(wire,clock):
    calls=wire([response(502)])
    job_deadline=clock.now+151
    with pytest.raises(d.DiscoveryError):d.discover(QUERY,job_deadline=job_deadline)
    assert len(calls)==1 and not clock.sleeps
    assert sum(calls[0]['timeout'])<=1
    assert job_deadline-clock.now>=d.PROCESSING_RESERVE_S


def test_no_request_without_processing_reserve(wire,clock):
    calls=wire([])
    with pytest.raises(d.DiscoveryError) as exc:d.discover(QUERY,job_deadline=clock.now+150)
    assert exc.value.code=='job_timeout' and not calls


def test_slow_request_exhausts_budget_without_extra_sleep_or_attempt(wire,clock):
    def timeout():
        clock.now+=9
        raise requests.ReadTimeout('Synthetic timeout consuming budget')
    calls=wire([timeout])
    with pytest.raises(d.DiscoveryError) as exc:d.discover(QUERY,budget_s=9)
    assert exc.value.code=='archive_timeout' and len(calls)==1 and not clock.sleeps


def test_progress_callback_cannot_make_sleep_overrun_deadline(wire,clock):
    calls=wire([response(502)])
    def progress(message):
        if 'Retrying discovery' in message:clock.now+=89
    with pytest.raises(d.DiscoveryError):d.discover(QUERY,progress)
    assert len(calls)==1 and not clock.sleeps


def test_public_budget_caps_global_setting(wire,clock):
    calls=wire([response(502)]*6)
    with pytest.raises(d.DiscoveryError):d.discover(QUERY,budget_s=60)
    assert len(calls)==5 and clock.sleeps==[2,4,8,16]


def test_transport_blocks_hidden_requests_redirects_and_retries(wire,clock):
    calls=wire([response()])
    with d.AttemptSession(clock.now+90) as session:
        assert session.get_adapter(d.SIA_URL).max_retries.total==0
        session.get(d.SIA_URL)
        with pytest.raises(d.DiscoveryError):session.get(d.SIA_URL)
    assert len(calls)==1 and calls[0]['allow_redirects'] is False


def test_response_byte_cap(wire,clock,monkeypatch):
    monkeypatch.setattr(d,'MAX_RESPONSE_BYTES',10)
    calls=wire([response()])
    with pytest.raises(d.DiscoveryError) as exc:d.discover(QUERY)
    assert exc.value.code=='archive_invalid_response' and len(calls)==1
