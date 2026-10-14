# Führt den Prüfstand (werkzeuge/pruefen.html) in Edge ohne Fenster aus und fasst das Ergebnis zusammen.
# Voraussetzung: Vorschau läuft (python -I werkzeuge/serve.py <projektordner> 8766).
# Aufruf: python -I werkzeuge/pruefen.py <projektordner> [seiten] [breiten]
import json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(sys.argv[1])
SEITEN = sys.argv[2] if len(sys.argv) > 2 else 'index,hoertest,hoersysteme,leistungen,gehoerschutz,ueber-uns,kontakt,jobs,anzeige,impressum,datenschutz'
BREITEN = sys.argv[3] if len(sys.argv) > 3 else '360,375,768,1024,1440'
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
PROFIL = os.path.join(ROOT, 'werkzeuge', '_edge')

url = f'http://localhost:8766/werkzeuge/pruefen.html?seiten={SEITEN}&breiten={BREITEN}'
aus = subprocess.run([EDGE, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + PROFIL,
                      '--virtual-time-budget=240000', '--dump-dom', url],
                     capture_output=True, timeout=600)
html = aus.stdout.decode('utf-8', 'replace')
m = re.search(r'<pre id="ergebnis">(.*?)</pre>', html, re.S)
daten = json.loads(m.group(1))

probleme = 0
links = set()
for r in daten:
    links.update(r.pop('links'))
    meldung = []
    if r['ueberlauf'] > 0 or r['zuBreit']:
        meldung.append(f"ÜBERLAUF {r['ueberlauf']}px {r['zuBreit']}")
    if r.get('innen'):
        meldung.append(f"INNEN {r['innen']}")
    if r['bilderKaputt']:
        meldung.append(f"BILDER {r['bilderKaputt']}")
    if r['kleinsteSchrift'] < 14:
        meldung.append(f"SCHRIFT {r['kleinsteSchrift']}px")
    if r['kontrastFehler']:
        meldung.append(f"KONTRAST {r['kontrastFehler']}")
    if r['fremd']:
        meldung.append(f"FREMD {r['fremd']}")
    a, b = r['einbettungen'].split('/')
    if a != b:
        meldung.append(f"ZWEI-KLICK {r['einbettungen']}")
    if r['h1'] != 1:
        meldung.append(f"H1 {r['h1']}")
    probleme += len(meldung)
    print(f"{r['seite']:13} {r['breite']:5}  Höhe {r['hoehe']:6}  Schrift>={r['kleinsteSchrift']:4}  "
          f"Platzh. {r['platzhalter']:2}  Prüfen {r['pruefen']}  " + ('OK' if not meldung else ' | '.join(meldung)))

# interne Links und Sprungziele prüfen
for l in sorted(links):
    pfad, _, anker = l[2:].partition('#')
    datei = os.path.join(ROOT, (pfad or 'index') + ('' if pfad.endswith('.html') else '.html'))
    if not os.path.exists(datei):
        print('TOTER LINK', l); probleme += 1; continue
    if anker:
        with open(datei, encoding='utf-8') as f:
            if f'id="{anker}"' not in f.read():
                print('SPRUNGZIEL FEHLT', l); probleme += 1
print('Interne Links geprüft:', len(links), '| Probleme gesamt:', probleme)
