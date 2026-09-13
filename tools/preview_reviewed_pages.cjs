// Visual QA of the exported notebook itself; these screenshots are not outputs.
const {chromium}=require('playwright');
const path=require('path');
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:1200,height:1000},deviceScaleFactor:1});
  const base=path.resolve(__dirname,'..');
  const cases=[
    ['chapt5/5.1_Decay_analysis_I.html','hxystrip->Draw','decay-position'],
    ['chapt5/5.2_Decay_analysis_II.html','TF1 *fdecay1','decay-fit'],
    ['chapt4/4.2_gamma-gamma_background_matrix.html','gate \\ peak','coincidence-table']
  ];
  for(const [rel,text,name] of cases){
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto('file://'+path.join(base,rel),{waitUntil:'load',timeout:60000});
    await page.waitForFunction(()=>[...document.querySelectorAll('[id^="root_plot_"]')].some(e=>e.querySelector('svg,canvas')),{timeout:30000}).catch(()=>{});
    const target=page.locator('.jp-Cell').filter({hasText:text}).first();
    await target.scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(base,'work',name+'-qa.png')});
    const counts=await page.evaluate(()=>({
      roots:document.querySelectorAll('[id^="root_plot_"]').length,
      drawn:[...document.querySelectorAll('[id^="root_plot_"]')].filter(e=>e.querySelector('svg,canvas')).length,
      tableWidths:[...document.querySelectorAll('.lecture-table-scroll')].map(e=>[e.clientWidth,e.scrollWidth])
    }));
    console.log(rel,counts,errors.slice(0,4));
    page.removeAllListeners('pageerror');
  }
  await browser.close();
})();
