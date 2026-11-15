import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'
import {challengeTargets} from './targets'
import SkyFrame from './SkyFrame'
import SpectralExplorer from './SpectralExplorer'
import ComparisonEvidence from './ComparisonEvidence'
import ObservationChart from './ObservationChart'
import type { Session } from './session'
import { readLink, restoreView, sessionLink, inventoryDisclosure } from './session'
import { exportEvidence } from './evidence'
const showcaseOnly=import.meta.env.VITE_SHOWCASE_ONLY==='true'
export default function App() {
 const [initialLink]=useState(()=>readLink(location.search))
 const [screen,setScreen]=useState<'search'|'viewer'|'library'|'spectral'>(()=>initialLink.id?'viewer':'search')
 const [spectralChannel,setSpectralChannel]=useState(()=>{const n=Number(initialLink.params.get('channel'));return Number.isInteger(n)&&n>=1&&n<=102?n:27})
 const controlPanel=useRef<HTMLDivElement>(null)
 useEffect(()=>{controlPanel.current?.scrollTo({top:0,behavior:'auto'})},[screen])
 const [ra,setRa]=useState(String(initialLink.query.ra)), [dec,setDec]=useState(String(initialLink.query.dec)), [fov,setFov]=useState(String(initialLink.query.fov))
 const [session,setSession]=useState<Session|null>(null),[index,setIndex]=useState(0),[playing,setPlaying]=useState(false),[speed,setSpeed]=useState(800),[zoom,setZoom]=useState(1)
 const [pan,setPan]=useState({x:0,y:0}),[error,setError]=useState(initialLink.invalidId?'Invalid session link. Check the coordinates and run a new search.':''),[busy,setBusy]=useState(false),[examples,setExamples]=useState<{id:string;query?:{ra:number;dec:number;fov:number};frames?:number;partial?:boolean;label?:string;description?:string;preview?:string;start?:string;end?:string}[]>([])
 const [offline,setOffline]=useState(showcaseOnly)
 const [exampleId,setExampleId]=useState('')
 const [targetName,setTargetName]=useState('')
 const target=challengeTargets.find(t=>t.name===targetName)
 const [frameCount,setFrameCount]=useState(String(initialLink.query.frames))
 const [detector,setDetector]=useState(initialLink.query.detector===null?'auto':String(initialLink.query.detector))
 const [selectionMode,setSelectionMode]=useState<'temporal'|'wavelength_matched'>(initialLink.query.selection_mode)
 const [cacheReused,setCacheReused]=useState(false)
 const generation=useRef(0)
 const [shareMessage,setShareMessage]=useState(''),[shareUrl,setShareUrl]=useState(''),[exporting,setExporting]=useState(false)
 const [blinkPair,setBlinkPair]=useState<[number,number]|null>(null)
 const [smooth,setSmooth]=useState(true),[compare,setCompare]=useState(false),[reference,setReference]=useState(0),[pixels,setPixels]=useState(0)
 useEffect(()=>{if(showcaseOnly){fetch('/showcase/index.json').then(r=>{if(!r.ok)throw new Error('Showcase unavailable');return r.json()}).then(setExamples).catch(()=>setError('The hosted showcase could not be loaded. Please reload.'));return}fetch('/api/examples',{signal:AbortSignal.timeout(8000)}).then(r=>{if(!r.ok)throw new Error('API unavailable');return r.json()}).then(setExamples).catch(()=>{setOffline(true);fetch('/showcase/index.json').then(r=>{if(!r.ok)throw new Error('No bundled showcase');return r.json()}).then(setExamples).catch(()=>setError('API unavailable and no bundled example could be loaded.'))})},[])
 const frames=useMemo(()=>session?.frames??[],[session]), frame=frames[index]
 const pair=session?.diagnostics?.pairs.find(p=>(p.a===index&&p.b===reference)||(p.b===index&&p.a===reference))
 useEffect(()=>{if(!playing||frames.length<2)return;const t=setInterval(()=>setIndex(i=>blinkPair?(i===blinkPair[0]?blinkPair[1]:blinkPair[0]):(i+1)%frames.length),speed);return()=>clearInterval(t)},[playing,speed,frames.length,blinkPair])
 useEffect(()=>{frames.forEach(f=>{const image=new Image();image.src=f.image})},[frames])
 async function load(id:string,token:number,restore?:URLSearchParams){
  let result:Session
  try{if(showcaseOnly)throw new Error('Showcase mode');const r=await fetch(`/api/sessions/${id}`,{signal:AbortSignal.timeout(8000)});if(!r.ok)throw new Error('Session unavailable');result=await r.json()}
  catch{const cached=await fetch(`/showcase/${encodeURIComponent(id)}/manifest.json`,{signal:AbortSignal.timeout(8000)});if(!cached.ok)throw new Error('This saved session is unavailable or expired and has no bundled copy. The link’s coordinates remain in the form; run a new search when the backend is available. Live sessions use temporary storage.');result=await cached.json();if(token===generation.current)setOffline(true)}
  if(token!==generation.current)return
  setSession(result)
  if(result.status==='ready'){
   const state=restoreView(result,restore??new URLSearchParams())
   setScreen(restore?.get('mode')==='spectral'?'spectral':'viewer');setBusy(false);setPlaying(false);setBlinkPair(null);setIndex(state.index);setReference(state.reference);setCompare(state.compare);setSmooth(state.smooth);setZoom(state.zoom);setPan(state.pan);setSpeed(state.speed);setPixels(0);setShareUrl('');setShareMessage('')
   if(result.query){setRa(String(result.query.ra));setDec(String(result.query.dec));setFov(String(result.query.fov));setFrameCount(String(result.query.frames??6));setDetector(result.query.detector?String(result.query.detector):'auto');setSelectionMode(result.query.selection_mode??'temporal')}
   const recommendation=result.selection?.recommendations[0]
   if(result.selection?.mode==='wavelength_matched'&&recommendation&&!restore?.has('frame')){setIndex(recommendation.a);setReference(recommendation.b);setCompare(true)}
   if(restore&&['frame','reference'].some(key=>restore.has(key)&&!result.frames?.some(f=>`${f.collection}/${f.obs_id}/${f.detector}`===restore.get(key))))setShareMessage('A linked observation is missing; available frames are shown instead.')
  }
  else if(result.status==='failed'){setScreen('search');setBusy(false);setError(result.message??'Processing failed');if(result.query){setRa(String(result.query.ra));setDec(String(result.query.dec));setFov(String(result.query.fov));setFrameCount(String(result.query.frames??6));setDetector(result.query.detector?String(result.query.detector):'auto');setSelectionMode(result.query.selection_mode??'temporal')}}
  else setTimeout(()=>{if(token===generation.current)load(id,token,restore).catch(e=>{if(token===generation.current){setBusy(false);setError(String(e))}})},1500)
 }
 async function search(e:React.SubmitEvent<HTMLFormElement>){e.preventDefault();setScreen('search');if(offline){setError('Live search requires the backend. Cached mode only opens the bundled example.');return}setPlaying(false);setBusy(true);setError('');setCacheReused(false);setSession(null);setPixels(0);setIndex(0);setReference(0);const token=++generation.current
  try{const r=await fetch('/api/sessions',{signal:AbortSignal.timeout(15000),method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ra:Number(ra),dec:Number(dec),fov:Number(fov),frames:Number(frameCount),detector:detector==='auto'?null:Number(detector),selection_mode:selectionMode})});const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail));setCacheReused(!!data.reused);await load(data.id,token)}catch(e){setError(String(e));setBusy(false)}
 }
 useEffect(()=>{
  const {id,params}=initialLink
  if(id)load(id,++generation.current,params).catch(e=>{setError(String(e));setScreen('search')})
  // Stale requests are ignored using their generation token.
 },[initialLink])
 const view={index,reference,compare,smooth,zoom,pan,speed}
 useEffect(()=>{
  if(session?.status==='ready'&&frame){const url=new URL(sessionLink(session,{index,reference,compare,smooth,zoom,pan,speed}));if(screen==='spectral'){url.searchParams.set('mode','spectral');url.searchParams.set('channel',String(spectralChannel))}history.replaceState(null,'',url.toString())}
 },[session,frame,index,reference,compare,smooth,zoom,pan,speed,screen,spectralChannel])
 async function share(){
  if(!session)return
  const url=sessionLink(session,view);setShareUrl(url)
  try{await navigator.clipboard.writeText(url);setShareMessage('Link copied. It restores these observations and view settings while the session is retained.')}
  catch{setShareMessage('Copy the link below. It restores the view while the session is retained.')}
 }
 async function downloadEvidence(){
  if(!session)return
  setExporting(true);setShareMessage('Preparing an offline evidence card…')
  try{await exportEvidence(session,view);setShareMessage('Evidence card downloaded. Open the HTML file offline or print it to PDF.')}
  catch(e){setShareMessage(e instanceof Error?e.message:'Evidence export failed. Please retry.')}
  finally{setExporting(false)}
 }

 return <main className="observatory-app">
  <header className="site-header"><a className="brand" href="/" aria-label="TimeScope home"><span className="brand-symbol" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="9" stroke="currentColor" strokeWidth="1.7"/><path d="M16 1v8m0 14v8M1 16h8m14 0h8M7 7l5 5m8 8 5 5" stroke="currentColor" strokeWidth="1.7"/><circle cx="16" cy="16" r="2.7" fill="currentColor"/></svg></span><strong>TIME<span>SCOPE</span></strong></a><nav aria-label="Main navigation" className="workspace-navigation"><button type="button" aria-current={screen==='search'?'page':undefined} onClick={()=>setScreen('search')}>Coordinate search</button><button type="button" aria-current={screen==='viewer'?'page':undefined} onClick={()=>setScreen('viewer')}>Observation viewer</button><button type="button" disabled={!frame} aria-current={screen==='spectral'?'page':undefined} onClick={()=>setScreen('spectral')}>Spectral explorer</button><button type="button" aria-current={screen==='library'?'page':undefined} onClick={()=>setScreen('library')}>Observation library</button></nav><a className="mission-link" href="https://irsa.ipac.caltech.edu/Missions/spherex.html" target="_blank" rel="noreferrer">SPHEREx mission <span aria-hidden="true">↗</span></a></header>
  {screen==='spectral'&&session?.query?<SpectralExplorer field={session.query} channel={spectralChannel} onChannel={setSpectralChannel}/>:<div className="observatory-layout" data-screen={screen}>
   <div className="control-column" ref={controlPanel} role="region" tabIndex={0} aria-label={screen==='viewer'?'Observation analysis':screen==='library'?'Observation library':'Coordinate search'}>
    {screen==='search'&&<>
  <section className="search-section" aria-label="Coordinate search"><div className="section-heading search-heading"><h1>SPHEREx observations</h1><p>ICRS coordinates and square field width.</p></div>
  <div className="target-presets"><label>Challenge target<select aria-label="Challenge target" value={targetName} disabled={busy} onChange={e=>{setTargetName(e.target.value);const t=challengeTargets.find(t=>t.name===e.target.value);if(t){setRa(String(t.ra));setDec(String(t.dec));setFov(String(t.fov))}}}><option value="">Custom coordinates</option>{challengeTargets.map(t=><option key={t.name} value={t.name}>{t.name}</option>)}</select></label>{target&&<><small>Reference epoch: {target.epoch}. Positions are not propagated; source visibility is unverified.</small><button className="quiet" disabled={busy} onClick={()=>{setPlaying(false);setError('');setCacheReused(false);load(target.bundle,++generation.current).catch(e=>setError(String(e)))}}>Open bundled target sequence</button><small>Bundled observations: no fresh archive search. The bundle retains its actual recorded field width.</small></>}</div>
  <div className="field-presets" aria-label="Suggested search fields"><span>Suggested positions:</span><button className="quiet" disabled={busy||offline} onClick={()=>{setRa('210.80227');setDec('54.34895');setFov('6')}}>M101 · IRSA tutorial field</button><button className="quiet" disabled={busy||offline} onClick={()=>{setRa('270');setDec('65');setFov('8')}}>RA 270° · Dec +65°</button><small>Sets search inputs only. Coverage and source detection are not verified.</small></div>
  <form id="coordinate-search" onSubmit={search}><label>Right ascension · degrees<input type="number" required min="0" max="359.999999999" step="any" value={ra} onChange={e=>setRa(e.target.value)}/></label><label>Declination · degrees<input type="number" required min="-90" max="90" step="any" value={dec} onChange={e=>setDec(e.target.value)}/></label><label>Field width · arcmin<input type="number" required min="1" max="15" step="any" value={fov} onChange={e=>setFov(e.target.value)}/></label><label>Observation count<input aria-label="Observation count" type="number" min="2" max="12" required step="1" value={frameCount} onChange={e=>setFrameCount(e.target.value)}/></label><label>Detector<select aria-label="Detector selection" value={detector} onChange={e=>setDetector(e.target.value)}><option value="auto">Auto</option>{[1,2,3,4,5,6].map(d=><option key={d} value={d}>Detector {d}</option>)}</select></label><label className="selection-mode">Observation selection<select aria-label="Observation selection" value={selectionMode} onChange={e=>setSelectionMode(e.target.value as 'temporal'|'wavelength_matched')}><option value="temporal">Temporal coverage</option><option value="wavelength_matched">Wavelength-prioritized</option></select></label><button disabled={busy||offline}>{offline?'Live search unavailable':busy?'Processing…':'Search observations'}</button></form>
  <div className="context"><span>Coordinates in degrees; field width in arcminutes. Exact-query results may be reused. Source identification is unverified.</span>{examples[0]&&<button className="quiet" disabled={busy} onClick={()=>{setPlaying(false);setError('');setCacheReused(false);load(exampleId||examples[0].id,++generation.current).catch(e=>setError(String(e)))}}>Open cached real observations</button>}</div>
  {examples.length>0&&<label className="example-picker">Bundled observation sequences<select aria-label="Cached field" value={exampleId||examples[0].id} disabled={busy} onChange={e=>setExampleId(e.target.value)}>{examples.map(example=><option key={example.id} value={example.id}>{example.label?`${example.label} · `:''}{example.query?`RA ${example.query.ra}° · Dec ${example.query.dec}° · ${example.query.fov}′`:example.id}{example.frames?` · ${example.frames} observations`:''}{example.partial?' · partial sequence':''}</option>)}</select></label>}
  {offline&&<p className="offline" role="status">{showcaseOnly?'Hosted showcase · Cached real observations. Live coordinate search is not connected.':'Backend unavailable · Cached real-data showcase. Live coordinate search is disabled. Reload when the backend returns.'}</p>}
  {offline&&!showcaseOnly&&<p><a href="https://timescope-spherex.roanpaste16.chatgpt.site" target="_blank" rel="noreferrer">Open the independently hosted real-data showcase ↗</a></p>}
  {error&&<div role="alert" className="alert"><p>{error}</p>{!offline&&<button type="submit" form="coordinate-search" disabled={busy||offline}>Retry search</button>}</div>}
  </section>
  <footer><div className="footer-brand"><strong>TIME<span>SCOPE</span></strong><small>Data: NASA SPHEREx / IPAC IRSA.</small></div><span>{showcaseOnly?'Hosted showcase · No automated detections':'No automated detections'}</span></footer>
    </>}
    {screen==='viewer'&&<section className="analysis-workspace" aria-label="Scientific analysis">
     <div className="section-heading analysis-heading"><h1>Observation analysis</h1><p>{frame?'Acquisition times, wavelengths and source metadata.':'Select a field to begin.'}</p></div>
  {session?.status==='ready'&&frame&&<section className="evidence-toolbar" aria-label="Investigation evidence">
   <div className="evidence-title"><strong>Investigation evidence</strong></div>
   <div className="evidence-actions"><button className="download-evidence" disabled={exporting} onClick={downloadEvidence}>{exporting?'Preparing evidence…':'Download evidence card'}</button><button className="copy-evidence-link" onClick={share}>Copy view link</button></div>
   <p className="share-help">Links may expire. Evidence cards embed preview images for offline reading.</p>
   {shareUrl&&<label className="share-link">View link<input aria-label="View link" readOnly value={shareUrl} onFocus={e=>e.target.select()}/></label>}
   {shareMessage&&<p role="status">{shareMessage}</p>}
  </section>}
  {session?.cached_showcase&&<p className="offline" role="status">Bundled genuine SPHEREx observations. Opening this sequence did not perform fresh archive discovery.</p>}
  {cacheReused&&session?.status==='ready'&&<p className="offline" role="status">Reused retained exact-query results. No new archive retrieval was performed.</p>}
  {session?.discovery_cached&&<p className="offline" role="status">{inventoryDisclosure(session)} Inventory kind: {session.inventory_kind??session.discovery_provenance?.inventory_kind??'not recorded'}.</p>}
  {session?.temporary_session&&<p className="offline">Temporary live session: links can expire through timed cleanup, storage eviction, or an instance restart. Download an evidence card to keep this view.</p>}
  {session?.partial&&<p role="status" className="offline">Partial sequence: {frames.length} observations loaded; {session.failed_frames?.length??0} skipped. Available frames are shown; skipped observations are listed in the processing manifest.</p>}

  {session?.selection&&frame&&<section className="selection-summary" aria-label="Observation selection evidence"><h3>{session.selection.mode==='wavelength_matched'?'Wavelength-prioritized comparison':'Temporal coverage'}</h3><p>{session.selection.processed_candidates} usable candidates processed · {frames.length} observations selected. Wavelength estimates come from the approximate field-center visualization WCS.</p>{session.selection.recommendations[0]?<><p>Recommended within this pool: {frames[session.selection.recommendations[0].a]?.date} ↔ {frames[session.selection.recommendations[0].b]?.date} UTC · {session.selection.recommendations[0].time_separation_days?.toFixed(1)} days · {session.selection.recommendations[0].fractional_wavelength_difference==null?'unknown':`${(session.selection.recommendations[0].fractional_wavelength_difference*100).toFixed(3)}%`} wavelength separation.</p><button onClick={()=>{const rec=session.selection!.recommendations[0];setPlaying(false);setBlinkPair(null);setIndex(rec.a);setReference(rec.b);setCompare(true)}}>Inspect recommended pair</button></>:<p>No pair recommendation is available from these measurements.</p>}<details><summary>Selection method and limitations</summary><p>{session.selection.method}</p><p>{session.selection.limitations}</p></details></section>}
  <ObservationChart frames={frames} index={index} reference={reference} compare={compare} onSelect={i=>{setPlaying(false);setIndex(i)}}/>
  <section id="metadata" className="metadata-panel" aria-label="Observation metadata"><h2>Observation metadata</h2>{frame?<dl><dt>Acquired · UTC</dt><dd>{frame.date}</dd><dt>Wavelength at field center</dt><dd>{frame.wavelength_um_at_center?.toFixed(3)??'Unavailable'} µm</dd><dt>Release / detector</dt><dd>{frame.collection} / {frame.detector}</dd><dt>Usable output coverage</dt><dd>{(frame.coverage*100).toFixed(1)}%</dd><dt>Observation ID</dt><dd>{frame.obs_id}</dd>{typeof frame.cutout_cached==='boolean'&&<><dt>Cutout retrieval</dt><dd>{frame.cutout_cached?'Exact-request FITS cache':session?.cached_showcase?'FITS retrieved when this bundle was prepared':'FITS cutouts retrieved for this request'}</dd></>}</dl>:<p>Dates, wavelengths and source provenance will appear here.</p>}<details className="notice"><summary>Scientific limitations</summary><div><p>Different wavelengths can change an object's appearance. These frames are not validated for subtraction or discovery claims.</p><p>Checkerboard areas are masked or outside valid coverage. Images share one brightness scale.</p></div></details>{session?.discovery_limited&&<p>Saved-inventory subset: these exposures cover the requested center, but this is not a complete archive search.</p>}{session?.possibly_truncated&&<p>Search reached its 1,000-record limit; this is a subset.</p>}{frame&&<a href={frame.source_url} target="_blank" rel="noreferrer">Original NASA/IPAC FITS ↗</a>}{session?.id&&<a href={session.manifest_url??`/artifacts/${session.id}/manifest.json`} target="_blank" rel="noreferrer">Processing manifest ↗</a>}</section>

  {frames.length>0&&<div className="filmstrip" aria-label="Observation frames">{frames.map((f,i)=><button key={f.image} aria-label={`Select observation ${i+1}: ${f.date} UTC`} aria-pressed={i===index} onClick={()=>{setPlaying(false);setIndex(i)}}><img src={f.image} alt=""/><span>{f.date.slice(0,10)}</span><small>{f.wavelength_um_at_center?.toFixed(3)??'?'} µm</small></button>)}</div>}

     {frame&&<section className="analysis-panel" aria-label="Display and comparison diagnostics"><h2>Display and alignment</h2>
  <p className="display-note">{smooth?'Smooth mode interpolates the display only; it adds no scientific detail.':'Native pixels preserves output pixel edges.'} {pixels>0&&`${pixels} × ${pixels} output pixels · ${((session?.query?.fov??5)*60/pixels).toFixed(2)}″ per output pixel · ${zoom.toFixed(1)}× fit zoom`}</p>
  {compare&&pair&&<div className="diagnostic"><strong>Preliminary alignment check</strong><p>{pair.matched_peaks} matched bright peaks · {(pair.overlap_fraction*100).toFixed(1)}% common coverage</p><p>{pair.status==='preliminary'?`Median separation: ${pair.median_separation_pixels?.toFixed(2)} pixels (${pair.median_separation_arcsec?.toFixed(2)}″)`:'Too few matched peaks to summarize alignment.'}</p><p>Matches are limited to a 2-pixel radius and are not catalog-confirmed stationary stars. No quantitative comparison is enabled.</p></div>}
  {compare&&frame&&frames[reference]&&<p className="comparison-note">Current: {frame.wavelength_um_at_center?.toFixed(3)??'unknown'} µm · Reference: {frames[reference].wavelength_um_at_center?.toFixed(3)??'unknown'} µm. Center wavelengths only; quantitative compatibility is unverified. {index===reference?'Both panels show the same observation.':''}</p>}

{compare&&frame&&frames[reference]&&<ComparisonEvidence current={frame} reference={frames[reference]} pair={pair}/>}

     </section>}
     {!frame&&<button className="quiet" type="button" onClick={()=>setScreen('search')}>Open coordinate search →</button>}
    </section>}
    {screen==='library'&&<>
  {examples.some(e=>e.label)&&<section id="fields" className="library-section" aria-label="Explore real fields"><div className="section-heading"><h2>Bundled observation sequences</h2><p>SPHEREx images available without live archive discovery.</p></div><div className="example-gallery">{examples.filter(e=>e.label).map(example=><button key={example.id} disabled={busy} onClick={()=>{setPlaying(false);setError('');setExampleId(example.id);setCacheReused(false);load(example.id,++generation.current).catch(e=>{setError(String(e));setScreen('search')})}}><img src={example.preview} alt=""/><div><strong>{example.label}</strong><p>{example.description}</p><small>{example.frames} observations · {example.start?.slice(0,10)} — {example.end?.slice(0,10)}{example.partial?' · partial':''}</small><span>Open field →</span></div></button>)}</div></section>}
  <footer><div className="footer-brand"><strong>TIME<span>SCOPE</span></strong><small>Data: NASA SPHEREx / IPAC IRSA.</small></div><span>{showcaseOnly?'Hosted showcase · No automated detections':'No automated detections'}</span></footer>
    </>}
   </div>
  <aside id="workspace" className="fixed-viewer" aria-label="Observation viewer">
   <div className="instrument-header"><span className="instrument-id"><span aria-hidden="true"/> SPHEREx IMAGE VIEWER</span><span>{frame?`FRAME ${String(index+1).padStart(2,'0')} / ${String(frames.length).padStart(2,'0')}`:'NO DATA'}</span></div>
   <div className="viewer-field">{frame&&session?.query?<><span>RA {session.query.ra}° · Dec {session.query.dec}° · {session.query.fov}′</span><span>{frame.wavelength_um_at_center?.toFixed(3)??'—'} µm</span></>:<span>ICRS · north up, east left</span>}</div>
   <div className="viewer-options">  <div className="view-options"><label>Rendering<select disabled={!frame} aria-label="Rendering" value={smooth?'smooth':'native'} onChange={e=>setSmooth(e.target.value==='smooth')}><option value="smooth">Smooth</option><option value="native">Native pixels</option></select></label><label>View<select disabled={!frame} aria-label="View mode" value={compare?'compare':'single'} onChange={e=>{setPlaying(false);setBlinkPair(null);setCompare(e.target.value==='compare')}}><option value="single">Timeline</option><option value="compare">Side by side</option></select></label>{compare&&<label>Reference frame<select aria-label="Reference frame" value={reference} onChange={e=>{setPlaying(false);setBlinkPair(null);setReference(Number(e.target.value))}}>{frames.map((f,i)=><option key={f.image} value={i}>{f.date}</option>)}</select></label>}</div>
<div className="controls extended-controls"><button disabled={frames.length<2} onClick={()=>{setPlaying(false);setIndex(i=>i===0?frames.length-1:0)}}>Blink endpoints</button>{compare&&<button disabled={frames.length<2||(!playing&&index===reference)} onClick={()=>{if(playing&&blinkPair){setPlaying(false);setIndex(blinkPair[0])}else{setBlinkPair([index,reference]);setPlaying(true)}}}>{playing&&blinkPair?'Stop pair blink':'Blink selected pair'}</button>}<label>Speed<select aria-label="Playback speed" value={speed} onChange={e=>setSpeed(Number(e.target.value))}><option value={1200}>Slow</option><option value={800}>Normal</option><option value={350}>Fast</option></select></label></div>
</div>
  <div className={compare&&frame?'viewer-stage frame-pair':'viewer-stage'}>
  {frame?<SkyFrame src={frame.image} date={frame.date} label="Current" smooth={smooth} zoom={zoom} pan={pan} onPan={setPan} fov={session?.query?.fov??5} onSize={setPixels}/>:<div className="imagebox"><div className="empty"><span>◎</span><h2>{busy?session?.message??'Contacting archive':'No observations loaded'}</h2><p>{busy?'Search and processing are in progress.':'Enter coordinates or select a bundled observation sequence.'}</p></div></div>}
  {compare&&frames[reference]&&<SkyFrame src={frames[reference].image} date={frames[reference].date} label="Reference" smooth={smooth} zoom={zoom} pan={pan} onPan={setPan} fov={session?.query?.fov??5}/>}
  </div>

   <div className="viewer-playback">
  <div className="controls"><button disabled={!frame} onClick={()=>{setPlaying(false);setIndex(i=>(i-1+frames.length)%frames.length)}} aria-label="Previous frame">←</button><button disabled={frames.length<2} onClick={()=>{setBlinkPair(null);setPlaying(!playing)}}>{playing?'Pause':'Play'}</button><button disabled={!frame} onClick={()=>{setPlaying(false);setIndex(i=>(i+1)%frames.length)}} aria-label="Next frame">→</button></div>

  <input aria-label="Observation timeline" type="range" min="0" max={Math.max(0,frames.length-1)} value={index} disabled={!frame} onChange={e=>{setPlaying(false);setIndex(Number(e.target.value))}}/>

   <div className="viewer-zoom">  <div className="context zoom-controls"><label>Zoom <input aria-label="Zoom" type="range" min="1" max="5" step="0.1" value={zoom} onChange={e=>setZoom(Number(e.target.value))}/></label><button className="quiet" onClick={()=>{setZoom(1);setPan({x:0,y:0})}}>Reset view</button></div></div>
   <span className="viewer-date">{frame?`${frame.date} UTC`:'No observations loaded'}</span></div>
  </aside>
  </div>}
 </main>
}
