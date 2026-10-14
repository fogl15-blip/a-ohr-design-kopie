# Setzt die gemeinsamen Bausteine aus werkzeuge/teile/*.html in alle Seiten ein.
# In den Seiten stehen Marken wie <!-- TEIL:kopf --> … <!-- /TEIL:kopf -->; alles dazwischen wird ersetzt.
# Den aktiven Menüpunkt bestimmt <body data-seite="…"> (passend zu data-nav im Menü).
# Kopf, Fuß, Anruf-Kachel also nur in werkzeuge/teile ändern und danach ausführen:
#   python -I werkzeuge/bauen.py <projektordner>
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
TEILE = os.path.join(ROOT, 'werkzeuge', 'teile')
SICHERUNG = os.path.join(ROOT, '_Sicherung', 'vor_Neuauflage_2026-10-14')

teile = {}
for n in os.listdir(TEILE):
    if n.endswith('.html'):
        with open(os.path.join(TEILE, n), encoding='utf-8') as f:
            teile[n[:-5]] = f.read().rstrip('\n')

MARKE = re.compile(r'(<!-- TEIL:([a-z-]+) -->)(.*?)(<!-- /TEIL:\2 -->)', re.S)
# Einmalig: Rechtstexte unverändert aus dem gesicherten Altstand übernehmen
RECHT = re.compile(r'%%RECHTSTEXT:([a-z]+)%%')


def rechtstext(name):
    with open(os.path.join(SICHERUNG, name + '.html'), encoding='utf-8') as f:
        alt = f.read()
    m = re.search(r'<div class="legal-content">(.*?)</div>\s*</div>\s*</section>', alt, re.S)
    if not m:
        raise SystemExit('Rechtstext nicht gefunden: ' + name)
    return m.group(1).strip('\n')


for name in sorted(os.listdir(ROOT)):
    if not name.endswith('.html'):
        continue
    pfad = os.path.join(ROOT, name)
    with open(pfad, encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'<body[^>]*\bdata-seite="([^"]*)"', html)
    seite = m.group(1) if m else ''

    def einsetzen(t):
        teil = teile[t.group(2)]
        if seite:
            teil = re.sub(r'(<a\b[^>]*\bdata-nav="%s")' % re.escape(seite), r'\1 aria-current="page"', teil)
        return t.group(1) + '\n' + teil + '\n' + t.group(4)

    neu, n = MARKE.subn(einsetzen, html)
    neu, r = RECHT.subn(lambda t: rechtstext(t.group(1)), neu)
    if neu != html:
        with open(pfad, 'w', encoding='utf-8', newline='\n') as f:
            f.write(neu)
    print(f'{name:22} {n} Teile' + (', Rechtstext eingesetzt' if r else ''))
