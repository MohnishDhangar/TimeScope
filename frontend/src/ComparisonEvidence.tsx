import {comparisonEvidence} from './comparison'
import type {Frame,Pair} from './session'
export default function ComparisonEvidence({current,reference,pair}:{current:Frame;reference:Frame;pair?:Pair}){
 return <section className="comparison-evidence" aria-label="Comparison evidence"><h3>Pairwise comparison evidence</h3><p>Acquisition, wavelength and alignment diagnostics for the selected observations. No quantitative compatibility score is inferred.</p><dl>{comparisonEvidence(current,reference,pair).map(row=><div key={row.label}><dt>{row.label}</dt><dd><strong>{row.value}</strong><span>{row.explanation}</span></dd></div>)}</dl></section>
}
