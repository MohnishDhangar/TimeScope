export type Frame = {image:string;date:string;obs_id:string;source_url:string;collection:string;detector:number;coverage:number;wavelength_um_at_center:number|null;bandwidth_um_at_center?:number|null;pipeline_version?:string|null;cutout_cached?:boolean;sha256?:string;unit?:string}
export type Pair = {a:number;b:number;matched_peaks:number;overlap_fraction:number;status:string;median_separation_pixels:number|null;median_separation_arcsec:number|null}
export type Recommendation = {a:number;b:number;time_separation_days:number|null;fractional_wavelength_difference:number|null;absolute_wavelength_difference_um:number|null;approximate_bandwidth_separation:number|null;common_coverage:number|null}
export type Session = {status:string;selection?:{mode:string;method:string;candidate_attempts:number;processed_candidates:number;selected_frames:number;limitations:string;recommendations:Recommendation[]};discovery_cached?:boolean;inventory_kind?:'runtime-cache'|'bundled-historical';discovery_provenance?:{inventory_retrieved_utc?:string;inventory_kind?:'runtime-cache'|'bundled-historical'};temporary_session?:boolean;expires_utc?:string;discovery_limited?:boolean;partial?:boolean;requested_frames?:number;failed_frames?:{reason:string}[];retryable?:boolean;cached_showcase?:boolean;manifest_url?:string;diagnostics?:{pairs:Pair[]};id?:string;message?:string;frames?:Frame[];warnings?:string[];possibly_truncated?:boolean;query?:{ra:number;dec:number;fov:number;frames?:number;detector?:number|null;selection_mode?:'temporal'|'wavelength_matched'}}
export type ViewState = {index:number;reference:number;compare:boolean;smooth:boolean;zoom:number;pan:{x:number;y:number};speed:number}

// A release + observation + detector identifies a frame independently of its array index.
export function frameKey(frame:Frame) { return `${frame.collection}/${frame.obs_id}/${frame.detector}` }
function bounded(value:string|null,min:number,max:number,fallback:number) {
 const n=value===null||value.trim()===''?NaN:Number(value)
 return Number.isFinite(n)&&n>=min&&n<=max?n:fallback
}
export function readLink(search:string) {
 const p=new URLSearchParams(search)
 const id=p.get('session')
 const query={ra:bounded(p.get('ra'),0,359.999999999,133.79512917),dec:bounded(p.get('dec'),-90,90,-7.24514722),fov:bounded(p.get('fov'),1,15,5),frames:Math.round(bounded(p.get('frames'),2,12,6)),detector:[1,2,3,4,5,6].includes(Number(p.get('detector')))?Number(p.get('detector')):null,selection_mode:p.get('selection_mode')==='wavelength_matched'?'wavelength_matched' as const:'temporal' as const}
 return {id:id&&/^[a-f0-9]{32}$/.test(id)?id:null,invalidId:!!id&&!/^[a-f0-9]{32}$/.test(id),query,params:p}
}
export function restoreView(session:Session,p:URLSearchParams):ViewState {
 const frames=session.frames??[]
 const find=(key:string|null,fallback:number)=>{const i=frames.findIndex(f=>frameKey(f)===key);return i>=0?i:fallback}
 return {index:find(p.get('frame'),0),reference:find(p.get('reference'),Math.max(0,frames.length-1)),compare:p.get('view')==='compare',smooth:p.get('render')!=='native',zoom:bounded(p.get('zoom'),1,5,1),pan:{x:bounded(p.get('x'),-20,20,0),y:bounded(p.get('y'),-20,20,0)},speed:[350,800,1200].includes(Number(p.get('speed')))?Number(p.get('speed')):800}
}
export function sessionLink(session:Session,view:ViewState) {
 const url=new URL(location.pathname,location.origin)
 const p=url.searchParams
 p.set('v','1')
 if(session.id)p.set('session',session.id)
 if(session.query)for(const [key,value] of Object.entries(session.query))if(value!==null&&['ra','dec','fov','frames','detector','selection_mode'].includes(key))p.set(key,String(value))
 const frames=session.frames??[]
 if(frames[view.index])p.set('frame',frameKey(frames[view.index]))
 if(frames[view.reference])p.set('reference',frameKey(frames[view.reference]))
 p.set('view',view.compare?'compare':'single');p.set('render',view.smooth?'smooth':'native')
 p.set('zoom',String(view.zoom));p.set('x',String(view.pan.x));p.set('y',String(view.pan.y));p.set('speed',String(view.speed))
 return url.href
}

export function inventoryDisclosure(session:Session) {
 if(!session.discovery_cached)return ''
 const date=session.discovery_provenance?.inventory_retrieved_utc
 return date?`Archive metadata snapshot retrieved ${date}. Observations released after that date may be missing. This is not a fresh archive discovery query.`:'Reused archive metadata; original retrieval date is not recorded. This is not a fresh archive discovery query.'
}
