# Sammelt alle Platzhalter (data-platzhalter) und Prüfstellen (data-pruefen) aus den Seiten
# und setzt sie als Liste in NEUAUFLAGE.md zwischen <!-- FEHLLISTE --> und <!-- /FEHLLISTE --> ein.
# Aufruf: python -I werkzeuge/fehlliste.py <projektordner>
import html, os, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(sys.argv[1])
SEITEN = [('index', 'Startseite'), ('hoertest', 'Hörtest & Ablauf'), ('hoersysteme', 'Hörgeräte'),
          ('leistungen', 'Service'), ('gehoerschutz', 'Gehörschutz'), ('ueber-uns', 'Über uns'),
          ('kontakt', 'Kontakt & Anfahrt')]


def text(s):
    s = re.sub(r'<svg.*?</svg>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


zeilen, n = [], 0
for datei, titel in SEITEN:
    with open(os.path.join(ROOT, datei + '.html'), encoding='utf-8') as f:
        quelle = f.read()
    funde = []
    for m in re.finditer(r'<(div|span|figure)\b[^>]*class="[^"]*platzhalter[^"]*"[^>]*data-platzhalter[^>]*>(.*?)</\1>', quelle, re.S):
        art = 'Foto' if 'platzhalter--bild' in m.group(0)[:200] else 'Text/Fakt'
        funde.append(f'| {art} | {text(m.group(2)).replace("Von Nico zu liefern: ", "")} |')
    for m in re.finditer(r'data-pruefen="([^"]+)"', quelle):
        funde.append(f'| Entwurf prüfen | {html.unescape(m.group(1))} |')
    if funde:
        zeilen.append(f'\n**{titel}** (`{datei}.html`)\n\n| Art | Was rein muss |\n|---|---|')
        zeilen.extend(funde)
        n += len(funde)

pfad = os.path.join(ROOT, 'NEUAUFLAGE.md')
with open(pfad, encoding='utf-8') as f:
    doku = f.read()
neu = re.sub(r'<!-- FEHLLISTE -->.*?<!-- /FEHLLISTE -->',
             '<!-- FEHLLISTE -->\n' + '\n'.join(zeilen) + '\n<!-- /FEHLLISTE -->', doku, flags=re.S)
with open(pfad, 'w', encoding='utf-8', newline='\n') as f:
    f.write(neu)
print('Einträge in der Fehlliste:', n)
