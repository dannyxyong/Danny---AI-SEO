// node render.js out.mp4 startFrame endFrame  — 30fps, 4 subframes/frame (180° shutter) blended with tmix
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
(async()=>{const [out,a,b]=process.argv.slice(2);const F0=+a,F1=+b,FPS=30,K=4,sub=1/(FPS*2*K);
 const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1920}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve('reel.html'));await p.evaluate(()=>window.ready);
 const vf=`tmix=frames=4:weights='1 1 1 1',select='eq(mod(n\\,4)\\,3)',setpts=N/30/TB`;
 const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate','120','-c:v','png','-i','-','-vf',vf,'-r','30','-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p',out]);
 ff.stderr.on('data',d=>process.stderr.write(d));
 for(let f=F0;f<F1;f++)for(let k=0;k<K;k++){const t=Math.min(14.999,Math.max(0,f/FPS+(k-1.5)*sub));await p.evaluate(t=>seek(t),t);
  const buf=await p.screenshot({type:'png'});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await br.close();console.log('done',out,F1-F0,errs[0]||'');})();
