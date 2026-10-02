from PIL import Image, ImageDraw, ImageFont
F='../fonts/'
def f(w,s): return ImageFont.truetype(F+f'Poppins-{w}.ttf',s)
def l(w,s): return ImageFont.truetype(F+f'Lato-{w}.ttf',s)
SEC=[("01","HOOK","0.0 – 2.2s",["0.35","1.90"],"Outline 'SCROLL' rows race up the feed with speed-skew, then spring-snap. One row lands as STOP. — its period is the hero dot (the one shape that never cuts)."),
("02","EVOLVE","2.2 – 4.6s",["3.85","4.25"],"The dot morphs into a live ad card, splits into A/B, the loser greys out, the winner gets the teal ring + check and fans into copies. Liquid stepper: TEST › LEARN › SCALE."),
("03","PLATFORMS","4.6 – 7.6s",["5.30","6.40"],"Winner card collapses into the gradient M core. 8 channels (Meta, Google, TikTok, LinkedIn, XHS, SEO, Web+CRO, Content) spring out onto counter-rotating 3D orbits. Core zooms through camera as a full-screen flash."),
("04","PROOF","7.6 – 10.6s",["8.60","9.80"],"Glass dashboard cards rise with 3D tilt. Counters roll to +40% bookings, −30% low-quality leads (Everkitchen) and 50+ home & living brands. Chart draws on; its tip is the hero dot."),
("05","REACH","10.6 – 12.8s",["11.30","12.10"],"The chart dot arcs across to Petaling Jaya HQ. Dot-grid map reveals radially; routes draw to Seoul, Bangkok, Singapore, Sydney with travelling light pulses."),
("06","BRAND + CTA","12.8 – 15.0s",["13.40","14.90"],"Network folds back into the hub, which grows into the M app-tile. MARVANT letters rise, EVOLUTIONS tracks in, CTA pill springs up, shimmers and gets a tap.")]
TW,TH=360,640; PAD=40; COLW=TW*2+16
cols=3; rows=2; CW=COLW+PAD; CH=TH+250
Wb=cols*CW+PAD; Hb=rows*CH+PAD+190
im=Image.new('RGB',(Wb,Hb),'#0e0c10'); d=ImageDraw.Draw(im)
d.text((PAD,46),"MARVANT EVOLUTIONS — 15s REEL · STORYBOARD",font=f(800,46),fill='white')
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
ts=["0.35","1.90","3.85","6.40","9.80","12.10","14.90"]; w,h=300,533
s=Image.new('RGB',(PAD+len(ts)*(w+16),h+150),'#0e0c10'); ds=ImageDraw.Draw(s)
ds.text((PAD,30),"INSTAGRAM SAFE-ZONE CHECK — mock Reels UI overlaid (red dashed = content limit)",font=f(700,30),fill='white')
for i,t in enumerate(ts):
    s.paste(Image.open(f'frames/t{t}_ig.png').resize((w,h),Image.LANCZOS),(PAD+i*(w+16),90))
    ds.text((PAD+i*(w+16)+w/2,90+h+28),f"{float(t):.2f}s",font=f(600,22),fill='#80e0e0',anchor='mm')
s.save('safe-zone-check.png',optimize=True)
