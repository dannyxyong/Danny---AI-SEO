// node render.js video out.mp4 [sub]      -> full render piped to ffmpeg (no audio)
// node render.js stills dir t1 t2 ...     -> PNG stills (with IG guides) at times
const {chromium}=require('playwright');const path=require('path');const {spawn}=require('child_process');const fs=require('fs');
(async()=>{
  const [mode,outp,...rest]=process.argv.slice(2);
  const b=await chromium.launch({args:['--disable-gpu-vsync','--force-color-profile=srgb']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text());});
  const q=mode==='stills'?'?guides&sub=1':`?sub=${rest[0]||6}`;
  await p.goto('file://'+path.resolve(__dirname,'reel.html')+q);await p.evaluate(()=>window.READY);
  if(mode==='stills'){fs.mkdirSync(outp,{recursive:true});
    for(const t of rest){await p.evaluate(f=>renderFrame(f),Math.round(+t*30));await p.locator('#c').screenshot({path:`${outp}/t${(+t).toFixed(2)}.png`});}
  } else {
    const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate','30','-c:v','png','-i','-','-c:v','libx264','-preset','slow','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',outp],{stdio:['pipe','inherit','inherit']});
    const t0=Date.now();
    for(let f=0;f<450;f++){
      await p.evaluate(f=>renderFrame(f),f);
      const buf=await p.locator('#c').screenshot({type:'png'});
      if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
      if(f%50===0)console.log('frame',f,((Date.now()-t0)/1000).toFixed(1)+'s');
    }
    ff.stdin.end();await new Promise(r=>ff.on('close',r));
  }
  if(errs.length)console.log('ERRORS',errs.slice(0,5));
  await b.close();
})();
