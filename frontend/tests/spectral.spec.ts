import {test,expect} from '@playwright/test'
import {validProduct} from '../src/spectral'
import {readFileSync} from 'node:fs'
const product=JSON.parse(readFileSync(new URL('../public/spectral/product.json',import.meta.url),'utf8'))
test('official cube metadata validates nonuniform channels and rejects malformed products',()=>{
 expect(validProduct(product)).toBe(true)
 expect(product.wavelengths_um).toHaveLength(102)
 expect(product.missing_indices).toEqual([50,51])
 expect(validProduct({...product,source:'https://untrusted.example'})).toBe(false)
 expect(validProduct({...product,wavelengths_um:[...product.wavelengths_um].reverse()})).toBe(false)
 expect(validProduct({...product,missing_indices:[102]})).toBe(false)
})
test('spectral controls preserve loaded field, disclose missing channels and export no invented measurements',async({page})=>{
 await page.route('**/spectral/frame.html?*',route=>route.fulfill({contentType:'text/html',body:`<script>parent.postMessage({type:'timescope-channel-ready',index:26},location.origin);addEventListener('message',e=>parent.postMessage({type:'timescope-channel-ready',index:e.data.index},location.origin))</script>`}))
 await page.goto('http://127.0.0.1:8000?session=23577cd786a24f24bedec59e7c5366ae')
 await page.getByRole('button',{name:'Spectral explorer',exact:true}).click()
 await expect(page.getByText('Channel 27 / 102')).toContainText('1.378')
 await page.getByRole('slider',{name:'Wavelength channel'}).fill('51')
 await expect(page.getByText(/Channel 51 is blank/)).toBeVisible()
 await expect(page.locator('iframe')).toBeHidden()
 const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'Download spectral record'}).click();const file=await downloaded;const record=JSON.parse(readFileSync((await file.path())!,'utf8'))
 expect(record.available).toBe(false);expect(record.measurements).toEqual([]);expect(record.field.dec).toBe(-7.24514722)
 await page.getByRole('button',{name:'Observation viewer',exact:true}).click()
 await expect(page.getByRole('img',{name:/Current: SPHEREx/})).toBeVisible()
})
test('spectral share URL restores channel and provider failure leaves temporal viewer usable',async({page})=>{
 await page.route('**/spectral/frame.html?*',route=>route.fulfill({contentType:'text/html',body:`<script>parent.postMessage({type:'timescope-error',message:'Synthetic provider failure fixture'},location.origin)</script>`}))
 await page.goto('http://127.0.0.1:8000?session=23577cd786a24f24bedec59e7c5366ae&mode=spectral&channel=63')
 await expect(page.getByRole('slider',{name:'Wavelength channel'})).toHaveValue('63')
 await expect(page.getByRole('alert')).toContainText('Synthetic provider failure fixture')
 await expect(page).toHaveURL(/mode=spectral/)
 await page.getByRole('button',{name:'Observation viewer',exact:true}).click()
 await expect(page.getByRole('img',{name:/Current: SPHEREx/})).toBeVisible()
})
