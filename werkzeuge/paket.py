# Packt das Projekt als ZIP für die Übergabe an einen anderen Claude (Ordner im ZIP: AOhr-Neuauflage/).
# Ausgelassen: _Eingang, _Ausgang, alle _Papierkorb, Edge-Profil, Roh-Screenshots, __pycache__.
# Aufruf: python -I werkzeuge/paket.py <projektordner> <zieldatei.zip>
import os, sys, zipfile

ROOT = os.path.abspath(sys.argv[1])
ZIEL = os.path.abspath(sys.argv[2])
WEG_ORDNER = {'_Eingang', '_Ausgang', '_Papierkorb', '_edge', '__pycache__'}
WEG_PFADE = {os.path.join('Screenshots', 'roh')}

os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
n = 0
with zipfile.ZipFile(ZIEL, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for ordner, unterordner, dateien in os.walk(ROOT):
        rel = os.path.relpath(ordner, ROOT)
        unterordner[:] = sorted(u for u in unterordner
                                if u not in WEG_ORDNER and os.path.normpath(os.path.join(rel, u)) not in WEG_PFADE)
        for datei in sorted(dateien):
            pfad = os.path.join(ordner, datei)
            if os.path.abspath(pfad) == ZIEL:
                continue
            z.write(pfad, os.path.join('AOhr-Neuauflage', os.path.relpath(pfad, ROOT)).replace(os.sep, '/'))
            n += 1
with zipfile.ZipFile(ZIEL) as z:
    fehler = z.testzip()
print('Dateien:', n, '| Größe:', round(os.path.getsize(ZIEL) / 1024 / 1024, 1), 'MB | Prüfung:', 'ok' if fehler is None else 'FEHLER ' + fehler)
