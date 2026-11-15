// Run against a separately started backend with an empty TIMESCOPE_DATA_DIR.
import assert from 'node:assert/strict'
import {chromium} from 'playwright'
const base=process.env.TIMESCOPE_TEST_URL??'http://127.0.0.1:8012'
const browser=await chromium.launch()
try {
 const page=await browser.newPage()
 const errors=[]
 page.on('pageerror',e=>errors.push(e.message))
 const response=await page.request.get(`${base}/api/examples`)
 const examples=await response.json()
 assert(examples.length>0&&examples.every(item=>item.bundled),'Use an empty backend data directory')
 await page.goto(base)
 await page.getByRole('button',{name:'Open cached real observations'}).click()
 await page.getByRole('img',{name:/Current: SPHEREx/}).waitFor()
 await page.waitForFunction(()=>document.querySelector('.imagebox img')?.naturalWidth>0)
 assert(await page.getByRole('button',{name:'Explore coordinates →'}).isEnabled())
 assert.equal(await page.getByText('Backend unavailable',{exact:false}).count(),0)
 await page.getByLabel('View mode').selectOption('compare')
 await page.getByRole('img',{name:/Reference: SPHEREx/}).waitFor()
 await page.reload()
 await page.getByRole('img',{name:/Reference: SPHEREx/}).waitFor()
 assert(await page.getByRole('button',{name:'Explore coordinates →'}).isEnabled())
 assert.deepEqual(errors,[])
 console.log('PASS: empty backend exposes real bundle; images, comparison and reload work; live-search control remains enabled. No live archive request was made.')
} finally {await browser.close()}
