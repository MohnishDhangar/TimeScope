import {test,expect} from '@playwright/test'
import {comparisonEvidence,utcMillis} from '../src/comparison'
import type {Frame} from '../src/session'
const a:Frame={image:'/a.png',date:'2025-01-01T00:00:00',obs_id:'a',source_url:'https://example.com/a.fits',collection:'spherex_dr1',detector:2,coverage:.9,wavelength_um_at_center:1.2,unit:'MJy / sr'}

test('evidence does not convert matching metadata into scientific approval',()=>{
 const same=comparisonEvidence(a,a)
 expect(same.find(r=>r.label==='Observation identity')?.value).toBe('Same observation')
 expect(same.find(r=>r.label==='Center wavelength difference')?.value).toBe('0.0000 µm')
 expect(same.find(r=>r.label==='Quantitative subtraction')?.value).toContain('Unavailable')
 const missing=comparisonEvidence(a,{...a,obs_id:'b',date:'2025-01-03T00:00:00',wavelength_um_at_center:null,unit:undefined})
 expect(missing.find(r=>r.label==='Center wavelength difference')?.value).toBe('Unavailable')
 expect(missing.find(r=>r.label==='Time separation')?.value).toBe('2.00 days')
 expect(missing.find(r=>r.label==='Common valid coverage')?.value).toContain('Not measured')
 expect(utcMillis('2025-01-01T00:00:00')).toBe(utcMillis('2025-01-01T00:00:00Z'))
})

test('chart selection, selected pair blink, and exported comparison evidence',async({page})=>{
 const {readFile}=await import('node:fs/promises')
 await page.goto('http://127.0.0.1:8000?session=23577cd786a24f24bedec59e7c5366ae')
 await page.getByRole('button',{name:/Inspect chart observation 2:/}).focus()
 await page.keyboard.press('Enter')
 await expect(page.getByLabel('Observation timeline')).toHaveValue('1')
 await page.getByLabel('View mode').selectOption('compare')
 await page.getByLabel('Reference frame',{exact:true}).selectOption('3')
 const evidence=page.getByRole('region',{name:'Comparison evidence',exact:true})
 await expect(evidence).toContainText('Distinct observations')
 await expect(evidence).toContainText('Unavailable — validation incomplete')
 await page.getByLabel('Playback speed').selectOption('1200')
 await page.getByRole('button',{name:'Blink selected pair',exact:true}).click()
 await expect(page.getByLabel('Observation timeline')).toHaveValue('3',{timeout:3000})
 await page.getByRole('button',{name:'Stop pair blink',exact:true}).click()
 await expect(page.getByLabel('Observation timeline')).toHaveValue('1')
 const event=page.waitForEvent('download')
 await page.getByRole('button',{name:'Download evidence card'}).click()
 const download=await event
 const html=await readFile((await download.path())!,'utf8')
 expect(html).toContain('Comparison evidence')
 expect(html).toContain('Center wavelength difference')
 expect(html).toContain('Unavailable — validation incomplete')
 await page.getByLabel('Reference frame',{exact:true}).selectOption('1')
 await expect(evidence).toContainText('Same observation')
 await expect(page.getByRole('button',{name:'Blink selected pair',exact:true})).toBeDisabled()
 await page.setViewportSize({width:390,height:844})
 await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true)
})
