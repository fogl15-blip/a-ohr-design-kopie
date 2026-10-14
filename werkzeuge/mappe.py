# Fotografiert alle Seiten (Desktop 1440 px, Handy 390 px) und baut daraus eine PDF-Bildmappe fürs Handy.
# Voraussetzung: Vorschau läuft (Port 8766). Aufruf: python -I werkzeuge/mappe.py <projektordner>
import io, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(sys.argv[1])
W = os.path.join(ROOT, 'werkzeuge')
ROH = os.path.join(ROOT, 'Screenshots', 'roh')
OUT = os.path.join(ROOT, 'Screenshots')
os.makedirs(ROH, exist_ok=True)

SEITEN = [('index', 'Startseite'), ('hoertest', 'Hörtest & Ablauf'), ('hoersysteme', 'Hörgeräte'),
          ('leistungen', 'Service'), ('gehoerschutz', 'Gehörschutz'), ('ueber-uns', 'Über uns'),
          ('kontakt', 'Kontakt & Anfahrt'), ('anzeige', 'Anzeige (QR-Ziel)'), ('jobs', 'Jobs (nicht im Menü)'),
          ('impressum', 'Impressum')]

# 1) Höhen messen
aus = subprocess.run([sys.executable, '-I', os.path.join(W, 'pruefen.py'), ROOT, ','.join(s for s, _ in SEITEN), '390,1440'],
                     capture_output=True, timeout=900)
hoehen = {}
for zeile in aus.stdout.decode('utf-8', 'replace').splitlines():
    m = re.match(r'^(\S+)\s+(\d+)\s+H\S+\s+(\d+)', zeile)
    if m:
        hoehen[(m.group(1), int(m.group(2)))] = int(m.group(3))

# 2) Fotografieren
args = [f'{s}:{b}:{hoehen[(s, b)]}' for s, _ in SEITEN for b in (1440, 390)] + ['hoertest:390:0:menue']
subprocess.run([sys.executable, '-I', os.path.join(W, 'fotos.py'), ROOT, ROH] + args, timeout=1800)

# 3) Bildmappe: Desktop auf 1000 px verkleinert, Handy in doppelter Auflösung; lange Seiten in Stücke geteilt
schrift = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 30)
seiten_pdf = []


def stuecke(im, titel, hoch):
    teile = list(range(0, im.height, hoch))
    for i, y in enumerate(teile):
        st = im.crop((0, y, im.width, min(y + hoch, im.height)))
        band = Image.new('RGB', (im.width, 64), (28, 28, 26))
        ImageDraw.Draw(band).text((22, 14), f'{titel}  ({i + 1}/{len(teile)})', font=schrift, fill=(255, 255, 255))
        blatt = Image.new('RGB', (im.width, st.height + 64), (255, 255, 255))
        blatt.paste(band, (0, 0))
        blatt.paste(st.convert('RGB'), (0, 64))
        seiten_pdf.append(blatt)


for s, titel in SEITEN:
    d = Image.open(os.path.join(ROH, f'{s}_1440_ganz.png'))
    d = d.resize((1000, round(d.height * 1000 / 1440)), Image.LANCZOS)
    stuecke(d, f'{titel} · Desktop', 1500)
    if s == 'index':
        d.convert('RGB').save(os.path.join(OUT, '01_Startseite_Desktop.jpg'), quality=85, optimize=True)
    h = Image.open(os.path.join(ROH, f'{s}_390_ganz.png'))
    stuecke(h, f'{titel} · Handy', 1800)
    if s == 'index':
        h.crop((0, 0, h.width, min(h.height, 6400))).convert('RGB').save(os.path.join(OUT, '02_Startseite_Handy_oben.jpg'), quality=85, optimize=True)
m = Image.open(os.path.join(ROH, 'hoertest_390_menue.png'))
stuecke(m, 'Menü am Handy (geöffnet)', 1800)

ziel = os.path.join(OUT, 'A-Ohr_Neuauflage_Bildmappe.pdf')
seiten_pdf[0].save(ziel, save_all=True, append_images=seiten_pdf[1:], resolution=144, quality=72)
print('PDF-Seiten:', len(seiten_pdf), '| Größe:', round(os.path.getsize(ziel) / 1024 / 1024, 1), 'MB')
