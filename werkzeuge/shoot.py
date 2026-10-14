# Ganzseitige Screenshots mit Edge (headless) von der lokalen Vorschau (Port 8766).
# Aufruf: python shoot.py '{"index_1280":5900,"index_375":9700}' ['?param=wert']
#   Schlüssel = Seite_Breite, Wert = Seitenhöhe in px. Breiten < 500 laufen über einen iframe-Rahmen.
# Braucht Pillow (pip install pillow, am besten in einem venv). Ergebnis in shots/, in Kacheln geschnitten.
import io
import subprocess, sys, os, json
from PIL import Image
EDGE=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
S=os.path.dirname(os.path.abspath(__file__))  # Ausgabe: shots/ und edge-profile/ neben diesem Skript
heights=json.loads(sys.argv[1]); only=[a for a in sys.argv[2:] if not a.startswith('?')]
for key,h in heights.items():
    if only and key not in only: continue
    page,w=key.rsplit('_',1); w=int(w)
    url='http://localhost:8766/'+('' if page=='index' else page)+(sys.argv[2] if len(sys.argv)>2 and sys.argv[2].startswith('?') else '')
    out=os.path.join(S,'shots',key+'.png')
    winw=w
    if w<500:
        wrap=os.path.join(S,'wrap_'+key+'.html')
        io.open(wrap,'w',encoding='utf-8').write('<!doctype html><body style="margin:0"><iframe src="%s" style="border:0;width:%dpx;height:%dpx;display:block"></iframe>'%(url,w,h))
        url='file:///'+wrap.replace(chr(92),'/'); winw=600
    subprocess.run([EDGE,'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',
        '--user-data-dir='+os.path.join(S,'edge-profile'),f'--window-size={winw},{h}',
        '--virtual-time-budget=4000','--screenshot='+out,url],capture_output=True,timeout=120)
    im=Image.open(out); tile=1100 if w>500 else 1400
    n=0
    for y in range(0,im.height,tile):
        im.crop((0,y,w,min(y+tile,im.height))).save(os.path.join(S,'shots',f'{key}_{n}.png')); n+=1
    print(key, im.size, n)
