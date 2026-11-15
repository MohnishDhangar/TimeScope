"""One bounded discovery orchestrator; one wire request per route attempt.

Astroquery uses the documented query endpoint without hidden VOSI capabilities
requests. Requests adapters never retry or follow redirects. Only discover()
retries, across both clients together.
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import io
import logging
import math
import os
import random
import socket
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

import requests
from astropy.table import Table
from astroquery.ipac.irsa import IrsaClass
from pyvo.dal.sia2 import SIA2Service

from .errors import PipelineError

SIA_URL = 'https://irsa.ipac.caltech.edu/SIA'
MAX_ATTEMPTS = 6
PROCESSING_RESERVE_S = 150
MIN_REQUEST_S = 1
MAX_RESPONSE_BYTES = 16*1024*1024
RETRY_STATUSES = (429, 502, 503, 504)


class DiscoveryError(PipelineError):
    def __init__(self, message, code, retryable=False, *, status=None, retry_after=None):
        super().__init__(message, code, retryable)
        self.status = status
        self.retry_after = retry_after
        self.attempt_log = []


def _causes(exc):
    """Inspect wrapped requests/urllib3 errors without inferring DNS from HTTP."""
    pending=[exc]; seen=set()
    while pending:
        item=pending.pop()
        if id(item) in seen:continue
        seen.add(id(item))
        yield item
        pending.extend(x for x in (getattr(item,'__cause__',None),getattr(item,'__context__',None),
                                   getattr(item,'reason',None),*getattr(item,'args',())) if isinstance(x,BaseException))


def classify(exc):
    if isinstance(exc,DiscoveryError):return exc
    if isinstance(exc,requests.HTTPError) and exc.response is not None:
        status=exc.response.status_code
        retry_after=exc.response.headers.get('Retry-After')
        if status==429:
            return DiscoveryError('IRSA limited archive search requests. Please retry in a few minutes; your coordinates have been preserved.',
                                  'archive_rate_limited',True,status=status,retry_after=retry_after)
        if 500<=status<=599:
            return DiscoveryError(f'IRSA returned HTTP {status} while searching for observations. The archive search service is temporarily unavailable. Please retry in a few minutes.',
                                  'archive_http_5xx',status in RETRY_STATUSES,status=status,retry_after=retry_after)
        return DiscoveryError(f'IRSA rejected the observation query (HTTP {status}). Check the coordinates and query settings.',
                              'archive_query_rejected',False,status=status)
    if isinstance(exc,(requests.Timeout,TimeoutError)):
        return DiscoveryError('IRSA did not respond within the time limit; your coordinates have been preserved. Please retry in a few minutes.',
                              'archive_timeout',True)
    causes=list(_causes(exc))
    if any(isinstance(e,ConnectionResetError) or 'connection reset' in str(e).lower() for e in causes):
        return DiscoveryError('The connection to IRSA was reset during observation search. Please retry; your coordinates have been preserved.',
                              'archive_invalid_response',True)
    if any(isinstance(e,(socket.gaierror,ConnectionRefusedError)) or type(e).__name__ in ('NameResolutionError','NewConnectionError')
           or (isinstance(e,OSError) and e.errno in (101,113)) for e in causes):
        return DiscoveryError('A DNS or connection failure prevented reaching IRSA. Please retry; your coordinates have been preserved.',
                              'network_unreachable',True)
    return DiscoveryError('IRSA returned an invalid archive search response. Please try again later; your coordinates have been preserved.',
                          'archive_invalid_response',False)


class AttemptSession(requests.Session):
    """Strict single-request transport shared by Astroquery and direct SIA."""
    def __init__(self,deadline):
        super().__init__()
        self.deadline=deadline
        self.sent=0
        self.payload=None
        self.failure=None
        self.mount('https://',requests.adapters.HTTPAdapter(max_retries=0))

    def request(self,method,url,**kwargs):
        remaining=self.deadline-time.monotonic()
        if self.sent or method.upper()!='GET' or url.rstrip('?')!=SIA_URL:
            raise DiscoveryError('Unexpected archive client request was blocked.','archive_invalid_response')
        if remaining<MIN_REQUEST_S:raise requests.Timeout('Discovery deadline reached before request')
        self.sent+=1
        kwargs.update(timeout=(min(5,remaining/3),min(35,remaining*2/3)),
                      stream=True,allow_redirects=False)
        try:
            with super().request(method,url,**kwargs) as response:
                response.raise_for_status()
                if response.status_code!=200:
                    raise DiscoveryError('IRSA returned an unexpected HTTP response.','archive_invalid_response',status=response.status_code)
                chunks=[];size=0
                for chunk in response.iter_content(65536):
                    if time.monotonic()>=self.deadline:raise requests.Timeout('Discovery deadline reached while reading')
                    size+=len(chunk)
                    if size>MAX_RESPONSE_BYTES:
                        raise DiscoveryError('IRSA search response exceeded the supported size.','archive_invalid_response')
                    chunks.append(chunk)
                self.payload=b''.join(chunks)
                buffered=requests.Response()
                buffered.status_code=response.status_code
                buffered.headers=response.headers.copy()
                buffered.url=response.url
                buffered._content=self.payload
                buffered._content_consumed=True
                buffered.raw=io.BytesIO(self.payload)
                return buffered
        except Exception as exc:
            self.failure=exc
            raise


def parse_response(payload,method):
    try:
        root=ET.fromstring(payload)
    except (ET.ParseError,TypeError) as exc:
        raise DiscoveryError('IRSA returned an invalid VOTable response.','archive_invalid_response') from exc
    if root.tag.split('}')[-1]!='VOTABLE':
        raise DiscoveryError('IRSA did not return an observation VOTable.','archive_invalid_response')
    infos=[e for e in root.iter() if e.tag.split('}')[-1]=='INFO' and e.get('name')=='QUERY_STATUS']
    if any(e.get('value')=='ERROR' for e in infos):
        raise DiscoveryError('IRSA returned a query error. Check the coordinates and supported collection settings.','archive_query_rejected')
    try:
        table=Table.read(io.BytesIO(payload),format='votable',use_names_over_ids=True)
    except Exception as exc:
        raise DiscoveryError('IRSA returned an unreadable VOTable.','archive_invalid_response') from exc
    if not {'obs_id','obs_collection','t_min','access_url'}.issubset(table.colnames):
        raise DiscoveryError('IRSA observation metadata schema is missing required fields.','archive_schema_changed')
    try:
        if any(not str(row['obs_id']) or str(row['obs_collection']) not in ('spherex_dr1','spherex_qr3')
               or not math.isfinite(float(row['t_min'])) for row in table):
            raise ValueError('Invalid required metadata')
    except (ValueError,TypeError) as exc:
        raise DiscoveryError('IRSA observation metadata schema contains invalid required values.','archive_schema_changed') from exc
    for row in table:
        url=urlsplit(str(row['access_url']))
        if url.scheme!='https' or url.netloc!='irsa.ipac.caltech.edu' or not url.path.startswith('/ibe/data/spherex/'):
            raise DiscoveryError('IRSA observation metadata contains an unsupported data URL.','archive_schema_changed')
    table.meta.update(discovery_method=method,discovery_transport='One GET per attempt; redirects and transport retries disabled',
                      query_overflow=any(e.get('value')=='OVERFLOW' for e in infos))
    return table


def direct_sia(search,*,deadline):
    params=[('MAXREC','1000'),('COLLECTION','spherex_qr3'),('COLLECTION','spherex_dr1'),
            ('POS',f'CIRCLE {search.ra} {search.dec} {search.fov/120*math.sqrt(2)}')]
    with AttemptSession(deadline) as session:
        session.get(SIA_URL,params=params,headers={'Cache-Control':'no-cache'})
        return parse_response(session.payload,'direct-sia-v2')


def astroquery_sia(search,*,deadline):
    with AttemptSession(deadline) as session:
        client=IrsaClass()
        client._sia=SIA2Service(SIA_URL,session=session,check_baseurl=False)
        try:
            client.query_sia(pos=(search.ra,search.dec,search.fov/120*math.sqrt(2)),
                             collection=['spherex_dr1','spherex_qr3'],maxrec=1000)
        except Exception:
            if session.failure is not None:raise session.failure
            if session.payload is None:raise
            # Parse the actual response to classify deterministic VO errors.
        return parse_response(session.payload,'astroquery-sia-v2')


def _retry_after(value):
    if value is None:return None
    try:
        seconds=float(value)
    except (ValueError,TypeError):
        try:seconds=parsedate_to_datetime(value).timestamp()-time.time()
        except (ValueError,TypeError,OverflowError):return None
    return max(0,seconds) if math.isfinite(seconds) else None


def discover(search,progress=lambda _:None,*,job_deadline=None,budget_s=None):
    configured=float(os.getenv('TIMESCOPE_DISCOVERY_BUDGET_S','90'))
    if not math.isfinite(configured) or configured<0:raise ValueError('Invalid discovery budget configuration')
    budget=min(configured,90,budget_s if budget_s is not None else 90)
    started=time.monotonic()
    deadline=started+budget
    if job_deadline is not None:deadline=min(deadline,job_deadline-PROCESSING_RESERVE_S)
    progress('Searching SPHEREx DR1 and QR3 observations')
    history=[]
    last=DiscoveryError('The job has insufficient time for discovery while preserving processing time. Please retry.','job_timeout',True)
    routes=(('Astroquery SIA (explicit query endpoint)',astroquery_sia),('direct SIA',direct_sia))
    for index in range(MAX_ATTEMPTS):
        if deadline-time.monotonic()<MIN_REQUEST_S:break
        name,route=routes[index%len(routes)]
        progress(f'Trying {name} (attempt {index+1} of {MAX_ATTEMPTS})')
        attempt_started=time.monotonic()
        try:
            rows=route(search,deadline=deadline)
            if time.monotonic()>deadline:raise requests.Timeout('Discovery exceeded its allotted budget')
            rows.meta.update(discovery_attempts=index+1,discovery_failures=history,
                             discovery_elapsed_seconds=round(time.monotonic()-started,3))
            return rows  # A valid empty result is definitive; never fall back to a cache.
        except Exception as exc:
            last=classify(exc)
            history.append({'attempt':index+1,'route':name,'code':last.code,'http_status':last.status,
                            'exception_class':type(exc).__name__,'elapsed_seconds':round(time.monotonic()-attempt_started,3)})
            logging.warning('IRSA discovery attempt %d/%d route=%s code=%s status=%s duration=%.3fs',
                            index+1,MAX_ATTEMPTS,name,last.code,last.status,time.monotonic()-attempt_started,exc_info=True)
            if not last.retryable:break
            delay=min(30,2**(index+1))*random.uniform(.9,1.1)
            retry_after=_retry_after(last.retry_after)
            if retry_after is not None:delay=max(delay,retry_after)
            if index+1==MAX_ATTEMPTS or delay+MIN_REQUEST_S>deadline-time.monotonic():break
            reason=f'IRSA returned HTTP {last.status}.' if last.status else str(last)
            progress(f'{reason} Retrying discovery in {delay:.1f} s (attempt {index+2} of {MAX_ATTEMPTS})')
            # Recheck after progress callbacks before sleeping or making a request.
            if delay+MIN_REQUEST_S>deadline-time.monotonic():break
            time.sleep(delay)
    last.attempt_log=history
    last.elapsed_seconds=round(time.monotonic()-started,3)
    raise last
