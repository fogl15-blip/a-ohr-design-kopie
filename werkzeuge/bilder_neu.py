# Erzeugt die bearbeiteten Bilder der Neuauflage in img/neu/ (Originale bleiben unverändert).
# Aufruf: python -I werkzeuge/bilder_neu.py <projektordner>
import os, shutil, sys
from PIL import Image, ImageEnhance

ROOT = sys.argv[1]
SRC = os.path.join(ROOT, 'img')
OUT = os.path.join(SRC, 'neu')
os.makedirs(OUT, exist_ok=True)


def speichern(im, name, q=82):
    pfad = os.path.join(OUT, name)
    im.convert('RGB').save(pfad, 'JPEG', quality=q, optimize=True, progressive=True)
    print(name, im.size, round(os.path.getsize(pfad) / 1024), 'KB')


def sanft(im, kontrast=1.04, farbe=1.03, hell=1.02):
    im = ImageEnhance.Contrast(im).enhance(kontrast)
    im = ImageEnhance.Color(im).enhance(farbe)
    return ImageEnhance.Brightness(im).enhance(hell)


# Armin Lahr mit IdO: Porträt (Desktop-Hero) und Querformat (Handy)
armin = Image.open(os.path.join(SRC, 'Hero_01.jpg'))
speichern(armin, 'armin-lahr.jpg')
speichern(armin.crop((0, 40, 1200, 840)), 'armin-lahr-quer.jpg')

# Hörtest-Szene im Laden: Beine, Stuhl und Boden abgeschnitten, leicht aufgefrischt
szene = Image.open(os.path.join(SRC, 'Hero_02.jpg'))
speichern(sanft(szene.crop((0, 110, 1200, 910)), 1.06, 1.04, 1.03), 'hoertest-szene.jpg')

# IdO zwischen den Fingern (Service)
ido = Image.open(os.path.join(SRC, 'Fremdgeraete.jpg'))
speichern(ido.crop((0, 150, 1200, 1050)), 'ido-hand.jpg')

# Logos mit ASCII-Dateinamen (Inhalt unverändert)
shutil.copyfile(os.path.join(SRC, 'A&Ohr-Logo_schwarz.svg'), os.path.join(OUT, 'logo-schwarz.svg'))
shutil.copyfile(os.path.join(SRC, 'A-Ohr_Logo_weiß.png'), os.path.join(OUT, 'logo-weiss.png'))
print('Logos kopiert')
