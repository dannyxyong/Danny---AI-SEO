// node stills.js out_dir [--ig] t1 t2 ...
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const a=process.argv.slice(2);const out=a.shift();const ig=a[0]==='--ig'?(a.shift(),true):false;fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.goto('file://'+path.resolve('reel.html')+(ig?'?ig':''));await p.evaluate(()=>window.ready);
 for(const t of a){await p.evaluate(t=>seek(t),+t);await p.screenshot({path:`${out}/t${(+t).toFixed(2)}${ig?'_ig':''}.png`});}
 await b.close();console.log(errs.length?'ERR '+errs.join('\n'):'ok');})();
