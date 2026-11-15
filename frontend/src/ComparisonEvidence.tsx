import {comparisonEvidence} from './comparison'
import type {Frame,Pair} from './session'
export default function ComparisonEvidence({current,reference,pair}:{current:Frame;reference:Frame;pair?:Pair}){
 return <section className="comparison-evidence" aria-label="Comparison evidence"><h3>What does this pair tell us?</h3><p>Use these measurements to interpret the images. This is an evidence summary, not a compatibility score.</p><dl>{comparisonEvidence(current,reference,pair).map(row=><div key={row.label}><dt>{row.label}</dt><dd><strong>{row.value}</strong><span>{row.explanation}</span></dd></div>)}</dl></section>
}
