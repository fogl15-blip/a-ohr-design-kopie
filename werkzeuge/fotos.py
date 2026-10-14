# Screenshots der Vorschau (Port 8766) mit Edge ohne Fenster.
# Aufruf: python -I werkzeuge/fotos.py <projektordner> <ausgabeordner> seite:breite[:höhe] ...
#   Ohne Höhe: ein Bildschirm (Handy 844, Desktop 900). Mit Höhe: ganze Seite (Höhe aus pruefen.py).
#   Breiten unter 500 px laufen über werkzeuge/_rahmen.html und werden in doppelter Auflösung aufgenommen.
import os
import subprocess
import sys
from urllib.parse import quote
from PIL import Image

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
os.makedirs(OUT, exist_ok=True)
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
PROFIL = os.path.join(ROOT, 'werkzeuge', '_edge')

for arg in sys.argv[3:]:
    teile = arg.split(':')
    seite, _, frage = teile[0].partition('?')   # z. B. index?nummern=oben
    breite = int(teile[1])
    voll = len(teile) > 2 and teile[2] != '0'
    hoehe = int(teile[2]) if voll else (844 if breite < 500 else 900)
    aktion = teile[3] if len(teile) > 3 else ''
    schmal = breite < 500
    dpr = 2 if schmal else 1
    pfad = ('' if seite == 'index' else seite) + (f'?{frage}' if frage else '')
    if schmal:
        url = f'http://localhost:8766/werkzeuge/_rahmen.html?seite={quote(pfad)}&w={breite}&h={hoehe}&aktion={aktion}'
        fenster = (600, hoehe)
    else:
        url = f'http://localhost:8766/{pfad}'
        fenster = (breite, hoehe)
    name = (f'{seite}_{breite}' + ('_ganz' if voll else '') + (f'_{aktion}' if aktion else '')
            + (f"_{frage.replace('=', '-')}" if frage else '') + '.png')
    ziel = os.path.join(OUT, name)
    subprocess.run([EDGE, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                    '--user-data-dir=' + PROFIL, f'--window-size={fenster[0]},{fenster[1]}',
                    f'--force-device-scale-factor={dpr}', '--virtual-time-budget=6000',
                    '--screenshot=' + ziel, url], capture_output=True, timeout=240)
    im = Image.open(ziel)
    if schmal:
        im = im.crop((0, 0, breite * dpr, im.height))
        im.save(ziel)
    print(name, im.size)
