from PIL import Image, ImageDraw, ImageFont
F='../fonts/'
def f(w,s): return ImageFont.truetype(F+f'Poppins-{w}.ttf',s)
def l(w,s): return ImageFont.truetype(F+f'Lato-{w}.ttf',s)
SEC=[("01","HOOK","0.0 – 2.0s",["0.90","1.70"],"'Your customers now ask AI.' A prompt bar springs out of a dot and types 'Best interior designer in KL?' while ghost queries drift behind. Send button pressed."),
("02","THE PROBLEM","2.0 – 4.5s",["3.00","4.10"],"The bar unfolds into an AI answer card. Three competitors stream in with citations; 'Your Brand' slides in dashed, gets a red 'Not mentioned' and a shake. 'Is your brand in the answer?'"),
("03","MARVANT AI SEO","4.5 – 7.6s",["5.40","6.50"],"The card collapses into the gradient M core. ChatGPT, Gemini, Perplexity and AI Overviews orbit on top; Entity SEO, Schema, Answer content and Citations below. Core zooms through camera as a flash."),
("04","HOW IT WORKS","7.6 – 10.2s",["8.60","9.90"],"Three glass step cards rise in 3D: map your entities, answer-ready content, earn the citations. The hero dot travels the timeline ticking each step; engine chips light up."),
("05","THE PAYOFF","10.2 – 12.5s",["11.20","12.00"],"Callback: the dot grows back into the same AI answer — now 'Your Brand' is #1, teal-outlined, 'Top pick' with a source line and a light burst. 'Now AI recommends you.'"),
("06","BRAND + CTA","12.5 – 15.0s",["13.30","14.90"],"The answer card folds into the M app-tile. MARVANT rises letter by letter, EVOLUTIONS tracks in, 'AI SEO that gets you cited.' CTA pill springs, shimmers and gets tapped.")]
TW,TH=360,640; PAD=40; COLW=TW*2+16
cols=3; rows=2; CW=COLW+PAD; CH=TH+250
Wb=cols*CW+PAD; Hb=rows*CH+PAD+190
im=Image.new('RGB',(Wb,Hb),'#0e0c10'); d=ImageDraw.Draw(im)
d.text((PAD,46),"MARVANT AI SEO — 15s REEL · STORYBOARD v2",font=f(800,46),fill='white')
d.text((PAD,110),"1080×1920 · 30fps · 6 sections · one continuous hero shape · all copy inside the 840×1230 IG safe zone",font=l(400,26),fill='#aab3ef')
for i,(n,name,tc,ts,desc) in enumerate(SEC):
    x=PAD+(i%cols)*CW; y=190+(i//cols)*CH
    d.rounded_rectangle((x,y,x+44+len(n)*0,y+44),radius=22,fill='#7f92e2'); d.text((x+22,y+22),n,font=f(700,22),fill='#231f20',anchor='mm')
    d.text((x+58,y+22),name,font=f(800,30),fill='white',anchor='lm')
    d.text((x+COLW,y+22),tc,font=f(600,24),fill='#80e0e0',anchor='rm')
    for j,t in enumerate(ts):
        fr=Image.open(f'frames/t{t}.png').resize((TW,TH),Image.LANCZOS)
        fx=x+j*(TW+16); fy=y+60; im.paste(fr,(fx,fy))
        d.rounded_rectangle((fx+10,fy+TH-46,fx+96,fy+TH-12),radius=10,fill='#000000')
        d.text((fx+53,fy+TH-29),f"{float(t):.2f}s",font=f(600,20),fill='white',anchor='mm')
    # wrap desc
    words=desc.split(); lines=[]; cur=''
    fnt=l(400,22)
    for w in words:
        if d.textlength(cur+' '+w,font=fnt)>COLW: lines.append(cur); cur=w
        else: cur=(cur+' '+w).strip()
    lines.append(cur)
    for k,ln in enumerate(lines[:5]): d.text((x,y+TH+76+k*30),ln,font=fnt,fill='#d6d6e0')
im.save('storyboard.png',optimize=True)
# safe zone sheet
ts=["1.70","4.10","6.50","9.90","12.00","14.90"]; w,h=300,533
s=Image.new('RGB',(PAD+len(ts)*(w+16),h+150),'#0e0c10'); ds=ImageDraw.Draw(s)
ds.text((PAD,30),"INSTAGRAM SAFE-ZONE CHECK — mock Reels UI overlaid (red dashed = content limit)",font=f(700,30),fill='white')
for i,t in enumerate(ts):
    s.paste(Image.open(f'frames/t{t}_ig.png').resize((w,h),Image.LANCZOS),(PAD+i*(w+16),90))
    ds.text((PAD+i*(w+16)+w/2,90+h+28),f"{float(t):.2f}s",font=f(600,22),fill='#80e0e0',anchor='mm')
s.save('safe-zone-check.png',optimize=True)
