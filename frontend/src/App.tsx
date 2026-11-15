import { useEffect, useRef, useState } from 'react'
import './App.css'
import SkyFrame from './SkyFrame'
import ComparisonEvidence from './ComparisonEvidence'
import ObservationChart from './ObservationChart'
import type { Session } from './session'
import { readLink, restoreView, sessionLink } from './session'
import { exportEvidence } from './evidence'
const showcaseOnly=import.meta.env.VITE_SHOWCASE_ONLY==='true'
export default function App() {
 const initialLink=useRef(readLink(location.search))
 const [ra,setRa]=useState(String(initialLink.current.query.ra)), [dec,setDec]=useState(String(initialLink.current.query.dec)), [fov,setFov]=useState(String(initialLink.current.query.fov))
 const [session,setSession]=useState<Session|null>(null),[index,setIndex]=useState(0),[playing,setPlaying]=useState(false),[speed,setSpeed]=useState(800),[zoom,setZoom]=useState(1)
 const [pan,setPan]=useState({x:0,y:0}),[error,setError]=useState(''),[busy,setBusy]=useState(false),[examples,setExamples]=useState<{id:string;query?:{ra:number;dec:number;fov:number};frames?:number;partial?:boolean;label?:string;description?:string;preview?:string;start?:string;end?:string}[]>([])
 const [offline,setOffline]=useState(showcaseOnly)
 const [exampleId,setExampleId]=useState('')
 const generation=useRef(0)
 const [shareMessage,setShareMessage]=useState(''),[shareUrl,setShareUrl]=useState(''),[exporting,setExporting]=useState(false)
 const [blinkPair,setBlinkPair]=useState<[number,number]|null>(null)
 const [smooth,setSmooth]=useState(true),[compare,setCompare]=useState(false),[reference,setReference]=useState(0),[pixels,setPixels]=useState(0)
 useEffect(()=>{if(showcaseOnly){fetch('/showcase/index.json').then(r=>{if(!r.ok)throw new Error('Showcase unavailable');return r.json()}).then(setExamples).catch(()=>setError('The hosted showcase could not be loaded. Please reload.'));return}fetch('/api/examples',{signal:AbortSignal.timeout(8000)}).then(r=>{if(!r.ok)throw new Error('API unavailable');return r.json()}).then(setExamples).catch(()=>{setOffline(true);fetch('/showcase/index.json').then(r=>{if(!r.ok)throw new Error('No bundled showcase');return r.json()}).then(setExamples).catch(()=>setError('API unavailable and no bundled example could be loaded.'))})},[])
 const frames=session?.frames??[], frame=frames[index]
 const pair=session?.diagnostics?.pairs.find(p=>(p.a===index&&p.b===reference)||(p.b===index&&p.a===reference))
 useEffect(()=>{if(!playing||frames.length<2)return;const t=setInterval(()=>setIndex(i=>blinkPair?(i===blinkPair[0]?blinkPair[1]:blinkPair[0]):(i+1)%frames.length),speed);return()=>clearInterval(t)},[playing,speed,frames.length,blinkPair])
 useEffect(()=>{frames.forEach(f=>{const image=new Image();image.src=f.image})},[frames])
 async function load(id:string,token:number,restore?:URLSearchParams){
  let result:Session
  try{if(showcaseOnly)throw new Error('Showcase mode');const r=await fetch(`/api/sessions/${id}`,{signal:AbortSignal.timeout(8000)});if(!r.ok)throw new Error('Session unavailable');result=await r.json()}
  catch{const cached=await fetch(`/showcase/${encodeURIComponent(id)}/manifest.json`);if(!cached.ok)throw new Error('This saved session is unavailable and has no bundled copy. The link’s coordinates remain in the form; run a new search when the backend is available.');result=await cached.json();if(token===generation.current)setOffline(true)}
  if(token!==generation.current)return
  setSession(result)
  if(result.status==='ready'){
   const state=restoreView(result,restore??new URLSearchParams())
   setBusy(false);setPlaying(false);setBlinkPair(null);setIndex(state.index);setReference(state.reference);setCompare(state.compare);setSmooth(state.smooth);setZoom(state.zoom);setPan(state.pan);setSpeed(state.speed);setPixels(0);setShareUrl('');setShareMessage('')
   if(result.query){setRa(String(result.query.ra));setDec(String(result.query.dec));setFov(String(result.query.fov))}
   if(restore&&['frame','reference'].some(key=>restore.has(key)&&!result.frames?.some(f=>`${f.collection}/${f.obs_id}/${f.detector}`===restore.get(key))))setShareMessage('A linked observation is missing; available frames are shown instead.')
  }
  else if(result.status==='failed'){setBusy(false);setError(result.message??'Processing failed');if(result.query){setRa(String(result.query.ra));setDec(String(result.query.dec));setFov(String(result.query.fov))}}
  else setTimeout(()=>{if(token===generation.current)load(id,token,restore).catch(e=>{if(token===generation.current){setBusy(false);setError(String(e))}})},1500)
 }
 async function search(e:React.SubmitEvent<HTMLFormElement>){e.preventDefault();if(offline){setError('Live search requires the backend. Cached mode only opens the bundled example.');return}setPlaying(false);setBusy(true);setError('');setSession(null);setPixels(0);setIndex(0);setReference(0);const token=++generation.current
  try{const r=await fetch('/api/sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ra:Number(ra),dec:Number(dec),fov:Number(fov),frames:6})});const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail));await load(data.id,token)}catch(e){setError(String(e));setBusy(false)}
 }
 useEffect(()=>{
  const {id,invalidId,params}=initialLink.current
  if(invalidId)setError('Invalid session link. Check the coordinates and run a new search.')
  if(id)load(id,++generation.current,params).catch(e=>setError(String(e)))
  return ()=>{generation.current++}
 },[])
 const view={index,reference,compare,smooth,zoom,pan,speed}
 useEffect(()=>{
  if(session?.status==='ready'&&frame)history.replaceState(null,'',sessionLink(session,{index,reference,compare,smooth,zoom,pan,speed}))
 },[session,frame,index,reference,compare,smooth,zoom,pan,speed])
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

 return <main>
  <header><a className="brand" href="/">◉ <strong>TimeScope</strong></a><span>SPHEREx · Temporal sky explorer</span><a href="https://irsa.ipac.caltech.edu/Missions/spherex.html" target="_blank" rel="noreferrer">About the data ↗</a></header>
  <section className="intro"><p className="eyebrow">A DIFFERENT VIEW OF THE NIGHT SKY</p><h1>One patch of sky.<br/><em>Different moments.</em></h1><p>Explore real infrared observations, frame by frame.<br/>Compare what you see—and the wavelengths behind it.</p></section>
  {examples.some(e=>e.label)&&<section className="example-gallery" aria-label="Explore real fields">{examples.filter(e=>e.label).map(example=><button key={example.id} disabled={busy} onClick={()=>{setPlaying(false);setError('');setExampleId(example.id);load(example.id,++generation.current).catch(e=>setError(String(e)))}}><img src={example.preview} alt=""/><div><strong>{example.label}</strong><p>{example.description}</p><small>{example.frames} observations · {example.start?.slice(0,10)} — {example.end?.slice(0,10)}{example.partial?' · partial':''}</small><span>Open field →</span></div></button>)}</section>}
  <div className="field-presets" aria-label="Suggested search fields"><span>Try another field:</span><button className="quiet" disabled={busy||offline} onClick={()=>{setRa('210.80227');setDec('54.34895');setFov('6')}}>M101 · IRSA tutorial field</button><button className="quiet" disabled={busy||offline} onClick={()=>{setRa('270');setDec('65');setFov('8')}}>RA 270° · Dec +65°</button><small>Sets search inputs only. Coverage and source detection are not verified.</small></div>
  <form id="coordinate-search" onSubmit={search}><label>Right ascension · degrees<input type="number" required min="0" max="359.999999999" step="any" value={ra} onChange={e=>setRa(e.target.value)}/></label><label>Declination · degrees<input type="number" required min="-90" max="90" step="any" value={dec} onChange={e=>setDec(e.target.value)}/></label><label>Field width · arcmin<input type="number" required min="1" max="15" step="any" value={fov} onChange={e=>setFov(e.target.value)}/></label><button disabled={busy||offline}>{offline?'Live search unavailable':busy?'Processing…':'Explore coordinates →'}</button></form>
  <div className="context"><span>ICRS coordinates · Angles in degrees. Every search retrieves the requested field; source identification is unverified.</span>{examples[0]&&<button className="quiet" disabled={busy} onClick={()=>{setPlaying(false);setError('');load(exampleId||examples[0].id,++generation.current).catch(e=>setError(String(e)))}}>Open cached real observations</button>}</div>
  {examples.length>0&&<label className="example-picker">Cached fields · real observations<select aria-label="Cached field" value={exampleId||examples[0].id} disabled={busy} onChange={e=>setExampleId(e.target.value)}>{examples.map(example=><option key={example.id} value={example.id}>{example.label?`${example.label} · `:''}{example.query?`RA ${example.query.ra}° · Dec ${example.query.dec}° · ${example.query.fov}′`:example.id}{example.frames?` · ${example.frames} observations`:''}{example.partial?' · partial sequence':''}</option>)}</select></label>}
  {offline&&<p className="offline" role="status">{showcaseOnly?'Hosted showcase · Cached real observations. Live coordinate search is not connected.':'Backend unavailable · Cached real-data showcase. Live coordinate search is disabled. Reload when the backend returns.'}</p>}
  {error&&<div role="alert" className="alert"><p>{error}</p>{session?.retryable&&<button type="submit" form="coordinate-search" disabled={busy||offline}>Retry search</button>}</div>}
  {session?.partial&&<p role="status" className="offline">Partial sequence: {frames.length} observations loaded; {session.failed_frames?.length??0} skipped. Available frames are shown; skipped observations are listed in the processing manifest.</p>}
  {session?.status==='ready'&&frame&&<section className="evidence-toolbar" aria-label="Save this investigation">
   <div><strong>Observed field · ICRS</strong><p>RA {session.query?.ra}° · Dec {session.query?.dec}° · Width {session.query?.fov}′</p><small>These coordinates describe the loaded images, independently of edits to the search form.</small></div>
   <div className="evidence-actions"><button onClick={share}>Copy view link</button><button disabled={exporting} onClick={downloadEvidence}>{exporting?'Preparing evidence…':'Download evidence card'}</button></div>
   <p className="share-help">Links depend on this host retaining the session. Evidence cards embed the preview images for offline reading; they are not discovery reports.</p>
   {shareUrl&&<label className="share-link">View link<input aria-label="View link" readOnly value={shareUrl} onFocus={e=>e.target.select()}/></label>}
   {shareMessage&&<p role="status">{shareMessage}</p>}
  </section>}
  <section className="workspace"><div>
  <div className="view-options"><label>Rendering<select disabled={!frame} aria-label="Rendering" value={smooth?'smooth':'native'} onChange={e=>setSmooth(e.target.value==='smooth')}><option value="smooth">Smooth</option><option value="native">Native pixels</option></select></label><label>View<select disabled={!frame} aria-label="View mode" value={compare?'compare':'single'} onChange={e=>{setPlaying(false);setBlinkPair(null);setCompare(e.target.value==='compare')}}><option value="single">Timeline</option><option value="compare">Side by side</option></select></label>{compare&&<label>Reference frame<select aria-label="Reference frame" value={reference} onChange={e=>{setPlaying(false);setBlinkPair(null);setReference(Number(e.target.value))}}>{frames.map((f,i)=><option key={f.image} value={i}>{f.date}</option>)}</select></label>}</div>
  <p className="display-note">{smooth?'Smooth mode interpolates the display only; it adds no scientific detail.':'Native pixels preserves output pixel edges.'} {pixels>0&&`${pixels} × ${pixels} output pixels · ${((session?.query?.fov??5)*60/pixels).toFixed(2)}″ per output pixel · ${zoom.toFixed(1)}× fit zoom`}</p>
  <div className={compare&&frame?'frame-pair':''}>
  {frame?<SkyFrame src={frame.image} date={frame.date} label="Current" smooth={smooth} zoom={zoom} pan={pan} onPan={setPan} fov={session?.query?.fov??5} onSize={setPixels}/>:<div className="imagebox"><div className="empty"><span>◎</span><h2>{busy?session?.message??'Contacting archive':'Your observing window'}</h2><p>{busy?'Retrieving real FITS cutouts and aligning their sky coordinates.':'Search a field or open cached observations to begin.'}</p></div></div>}
  {compare&&frames[reference]&&<SkyFrame src={frames[reference].image} date={frames[reference].date} label="Reference" smooth={smooth} zoom={zoom} pan={pan} onPan={setPan} fov={session?.query?.fov??5}/>}
  </div>
  {compare&&pair&&<div className="diagnostic"><strong>Preliminary alignment check</strong><p>{pair.matched_peaks} matched bright peaks · {(pair.overlap_fraction*100).toFixed(1)}% common coverage</p><p>{pair.status==='preliminary'?`Median separation: ${pair.median_separation_pixels?.toFixed(2)} pixels (${pair.median_separation_arcsec?.toFixed(2)}″)`:'Too few matched peaks to summarize alignment.'}</p><p>Matches are limited to a 2-pixel radius and are not catalog-confirmed stationary stars. No quantitative comparison is enabled.</p></div>}
  {compare&&frame&&frames[reference]&&<p className="comparison-note">Current: {frame.wavelength_um_at_center?.toFixed(3)??'unknown'} µm · Reference: {frames[reference].wavelength_um_at_center?.toFixed(3)??'unknown'} µm. Center wavelengths only; quantitative compatibility is unverified. {index===reference?'Both panels show the same observation.':''}</p>}
  <div className="controls"><button disabled={!frame} onClick={()=>{setPlaying(false);setIndex(i=>(i-1+frames.length)%frames.length)}} aria-label="Previous frame">←</button><button disabled={frames.length<2} onClick={()=>{setBlinkPair(null);setPlaying(!playing)}}>{playing?'Pause':'Play'}</button><button disabled={!frame} onClick={()=>{setPlaying(false);setIndex(i=>(i+1)%frames.length)}} aria-label="Next frame">→</button><button disabled={frames.length<2} onClick={()=>{setPlaying(false);setIndex(i=>i===0?frames.length-1:0)}}>Blink endpoints</button>{compare&&<button disabled={frames.length<2||(!playing&&index===reference)} onClick={()=>{if(playing&&blinkPair){setPlaying(false);setIndex(blinkPair[0])}else{setBlinkPair([index,reference]);setPlaying(true)}}}>{playing&&blinkPair?'Stop pair blink':'Blink selected pair'}</button>}<label>Speed<select aria-label="Playback speed" value={speed} onChange={e=>setSpeed(Number(e.target.value))}><option value={1200}>Slow</option><option value={800}>Normal</option><option value={350}>Fast</option></select></label></div>
  <input aria-label="Observation timeline" type="range" min="0" max={Math.max(0,frames.length-1)} value={index} disabled={!frame} onChange={e=>{setPlaying(false);setIndex(Number(e.target.value))}}/>
  <ObservationChart frames={frames} index={index} reference={reference} compare={compare} onSelect={i=>{setPlaying(false);setIndex(i)}}/>
  {frames.length>0&&<div className="filmstrip" aria-label="Observation frames">{frames.map((f,i)=><button key={f.image} aria-label={`Select observation ${i+1}: ${f.date} UTC`} aria-pressed={i===index} onClick={()=>{setPlaying(false);setIndex(i)}}><img src={f.image} alt=""/><span>{f.date.slice(0,10)}</span><small>{f.wavelength_um_at_center?.toFixed(3)??'?'} µm</small></button>)}</div>}
  <div className="context"><span>{frame?`Observation ${index+1} of ${frames.length}`:'No observations loaded'}</span><label>Zoom <input aria-label="Zoom" type="range" min="1" max="5" step="0.1" value={zoom} onChange={e=>setZoom(Number(e.target.value))}/></label><button className="quiet" onClick={()=>{setZoom(1);setPan({x:0,y:0})}}>Reset view</button></div>{compare&&frame&&frames[reference]&&<ComparisonEvidence current={frame} reference={frames[reference]} pair={pair}/>}</div>
  <aside><p className="eyebrow">OBSERVATION NOTES</p><h2>Look closer.<br/>Compare carefully.</h2>{frame?<dl><dt>Acquired · UTC</dt><dd>{frame.date}</dd><dt>Wavelength at field center</dt><dd>{frame.wavelength_um_at_center?.toFixed(3)??'Unavailable'} µm</dd><dt>Release / detector</dt><dd>{frame.collection} / {frame.detector}</dd><dt>Usable output coverage</dt><dd>{(frame.coverage*100).toFixed(1)}%</dd><dt>Observation ID</dt><dd>{frame.obs_id}</dd></dl>:<p>Dates, wavelengths and source provenance will appear here.</p>}<div className="notice"><strong>Qualitative comparison</strong><p>Different wavelengths can change an object's appearance. These frames are not validated for subtraction or discovery claims.</p><p>Checkerboard areas are masked or outside valid coverage. Images share one brightness scale.</p></div>{session?.discovery_limited&&<p>Saved-inventory subset: these exposures cover the requested center, but this is not a complete archive search.</p>}{session?.possibly_truncated&&<p>Search reached its 1,000-record limit; this is a subset.</p>}{frame&&<a href={frame.source_url} target="_blank" rel="noreferrer">Original NASA/IPAC FITS ↗</a>}{session?.id&&<a href={session.manifest_url??`/artifacts/${session.id}/manifest.json`} target="_blank" rel="noreferrer">Processing manifest ↗</a>}</aside></section>
  <footer>Real observations from NASA SPHEREx / IPAC IRSA.<span>{showcaseOnly?'Hosted showcase · No automated detections':'Development preview · No automated detections'}</span></footer>
 </main>
}
