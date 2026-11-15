import {utcMillis} from './comparison'
import type {Frame} from './session'
export default function ObservationChart({frames,index,reference,compare,onSelect}:{frames:Frame[];index:number;reference:number;compare:boolean;onSelect:(i:number)=>void}){
 const points=frames.map((f,i)=>({i,t:utcMillis(f.date),w:f.wavelength_um_at_center})).filter((p):p is {i:number;t:number;w:number}=>Number.isFinite(p.t)&&typeof p.w==='number'&&Number.isFinite(p.w))
 if(points.length<2)return null
 const times=points.map(p=>p.t),waves=points.map(p=>p.w)
 const minT=Math.min(...times),maxT=Math.max(...times),minW=Math.min(...waves),maxW=Math.max(...waves)
 const x=(t:number)=>70+(t-minT)/Math.max(1,maxT-minT)*530
 const y=(w:number)=>160-(w-minW)/Math.max(.001,maxW-minW)*110
 return <section className="observation-chart" aria-label="Time and wavelength"><h3>Time and wavelength</h3><p>Horizontal: acquisition date. Vertical: wavelength at field center. Select a point to inspect that observation; this is not a light curve.</p><svg viewBox="0 0 660 210" aria-label="Observation dates versus center wavelengths">
 <path d="M70 40V175H610" fill="none" stroke="currentColor" opacity=".4"/>
 <text x="10" y="55">{maxW.toFixed(2)}</text><text x="10" y="165">{minW.toFixed(2)}</text><text x="10" y="25">µm</text>
 <text x="70" y="200">{new Date(minT).toISOString().slice(0,10)}</text><text x="600" y="200" textAnchor="end">{new Date(maxT).toISOString().slice(0,10)}</text>
 {points.map(p=><g key={p.i} role="button" tabIndex={0} aria-label={`Inspect chart observation ${p.i+1}: ${frames[p.i].date}, ${p.w.toFixed(3)} micrometers`} aria-pressed={p.i===index} onClick={()=>onSelect(p.i)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onSelect(p.i)}}}><circle cx={x(p.t)} cy={y(p.w)} r="13" fill="transparent"/><circle cx={x(p.t)} cy={y(p.w)} r={p.i===index?8:5} fill={p.i===index?'#a2e4d0':'#789ca7'} stroke={compare&&p.i===reference?'#e5c58a':'#0b1215'} strokeWidth={compare&&p.i===reference?3:1}/><title>Observation {p.i+1}: {p.w.toFixed(3)} µm</title></g>)}
 </svg><small>Mint: current observation{compare?' · Gold outline: reference':''}. Close center wavelengths alone do not establish compatibility.</small></section>
}
