import {frameKey} from './session'
import type {Frame, Pair} from './session'
export type EvidenceRow={label:string;value:string;explanation:string}
export function utcMillis(date:string){return Date.parse(/[zZ]$|[+-]\d\d:\d\d$/.test(date)?date:`${date}Z`)}
function finite(n:unknown):n is number{return typeof n==='number'&&Number.isFinite(n)}
export function comparisonEvidence(a:Frame,b:Frame,pair?:Pair):EvidenceRow[]{
 const days=Math.abs(utcMillis(b.date)-utcMillis(a.date))/86400000
 const delta=finite(a.wavelength_um_at_center)&&finite(b.wavelength_um_at_center)?Math.abs(a.wavelength_um_at_center-b.wavelength_um_at_center):null
 return [
  {label:'Observation identity',value:frameKey(a)===frameKey(b)?'Same observation':'Distinct observations',explanation:frameKey(a)===frameKey(b)?'Choose a different reference to compare acquisitions.':'Different acquisitions do not by themselves establish a temporal change.'},
  {label:'Time separation',value:Number.isFinite(days)?`${days.toFixed(2)} days`:'Unavailable',explanation:'Calculated from acquisition timestamps in UTC, not product creation dates.'},
  {label:'Center wavelength difference',value:delta===null?'Unavailable':`${delta.toFixed(4)} µm`,explanation:'A center value is not the full filter response. Equal center wavelengths would not prove spectral compatibility.'},
  {label:'Detector / release',value:`${a.detector} / ${a.collection} ↔ ${b.detector} / ${b.collection}`,explanation:'The filter wavelength varies with detector position. Sharing a detector or release is not a compatibility test.'},
  {label:'Science units',value:a.unit&&b.unit?`${a.unit} ↔ ${b.unit}`:'Unavailable',explanation:'Matching unit labels do not establish matched calibration, background or PSF.'},
  {label:'Common valid coverage',value:pair&&finite(pair.overlap_fraction)?`${(pair.overlap_fraction*100).toFixed(1)}%`:'Not measured for this pair',explanation:'The overlap of both validity masks. Missing data is not zero brightness.'},
  {label:'Measured geometry',value:pair?.status==='preliminary'&&finite(pair.median_separation_pixels)?`${pair.matched_peaks} bright-peak matches · ${pair.median_separation_pixels.toFixed(2)} px median offset`:'Insufficient or unavailable bright-peak matches',explanation:'Two-pixel matching radius; not catalog-confirmed stationary reference sources.'},
  {label:'Quantitative subtraction',value:'Unavailable — validation incomplete',explanation:'Requires spectral-response compatibility, PSF/background matching, catalog-based registration checks and justified uncertainty propagation.'},
 ]
}
