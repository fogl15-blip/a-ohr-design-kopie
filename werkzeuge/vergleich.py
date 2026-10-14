# Vergleichsbilder der offenen Design-Varianten (A/B) für Nico (Handy-tauglich).
# Aufruf: <venv-python> vergleich.py <ausgabeordner>
import io, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = sys.argv[1]
TMP = os.path.join(OUT, '_roh')
PROFILE = os.path.join(OUT, '_edge-profile')
os.makedirs(TMP, exist_ok=True)
BASE = dict(koepfe='rot', mobilhero='sand', motiv='mit', leiste='mit', footer='dunkel', panel='aus')
FONT_B = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 34)
FONT_T = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 44)


def shot(name, page, w, h, **var):
    p = dict(BASE, **var)
    url = 'http://localhost:8766/' + page + '?' + '&'.join(f'{k}={v}' for k, v in p.items())
    out = os.path.join(TMP, name + '.png')
    winw = w
    if w < 500:
        wrap = os.path.join(TMP, 'wrap_' + name + '.html')
        io.open(wrap, 'w', encoding='utf-8').write(
            '<!doctype html><body style="margin:0"><iframe src="%s" style="border:0;width:%dpx;height:%dpx;display:block"></iframe>' % (url, w, h))
        url = 'file:///' + wrap.replace('\\', '/')
        winw = 600
    subprocess.run([EDGE, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                    '--user-data-dir=' + PROFILE, f'--window-size={winw},{h}',
                    '--virtual-time-budget=5000', '--screenshot=' + out, url], capture_output=True, timeout=120)
    im = Image.open(out).convert('RGB')
    return im.crop((0, 0, w, im.height))


def label(im, text, color):
    bar = 64
    out = Image.new('RGB', (im.width, im.height + bar), 'white')
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, im.width, bar), fill=color)
    d.text((20, bar // 2), text, font=FONT_B, fill='white', anchor='lm')
    out.paste(im, (0, bar))
    return out


ONLY = sys.argv[2] if len(sys.argv) > 2 else None


def sheet(fname, title, parts, side_by_side):
    gap = 24
    if side_by_side:
        W = sum(p.width for p in parts) + gap * (len(parts) + 1)
        H = max(p.height for p in parts) + 2 * gap + 90
    else:
        W = max(p.width for p in parts) + 2 * gap
        H = sum(p.height for p in parts) + gap * (len(parts) + 1) + 90
    out = Image.new('RGB', (W, H), (232, 229, 224))
    d = ImageDraw.Draw(out)
    d.text((gap, 45), title, font=FONT_T, fill=(28, 28, 26), anchor='lm')
    x, y = gap, 90
    for p in parts:
        out.paste(p, (x, y))
        if side_by_side:
            x += p.width + gap
        else:
            y += p.height + gap
    out.save(os.path.join(OUT, fname), optimize=True)
    print(fname, out.size)


A, B = (28, 28, 26), (200, 16, 46)

# 1) Serviceleiste (Desktop)
sheet('1_serviceleiste.png', 'Frage 1 – Dunkle Serviceleiste oben (nur Desktop)', [
    label(shot('leiste_mit', '', 1280, 760), 'A  Mit Serviceleiste (jetzt)', B),
    label(shot('leiste_ohne', '', 1280, 760, leiste='ohne'), 'B  Ohne – Telefon-Knopf im Kopf (wie Runde 9)', A),
], False)

# 2) Footer (Desktop + Handy)
def footer(name, page, w, h, top, **var):
    im = shot(name, page, w, h, **var)
    return im.crop((0, max(0, top - 40), w, im.height))

sheet('2_footer_desktop.png', 'Frage 2 – Footer dunkel oder hell (Desktop)', [
    label(footer('foot_d', '', 1280, 5843, 5445), 'A  Dunkel (jetzt)', B),
    label(footer('foot_h', '', 1280, 5830, 5445, footer='hell'), 'B  Hell (wie Runde 9)', A),
], False)

sheet('2b_footer_handy.png', 'Frage 2 – Footer am Handy', [
    label(footer('foot_dm', '', 375, 9664, 9664 - 880), 'A  Dunkel (jetzt)', B),
    label(footer('foot_hm', '', 375, 9656, 9656 - 880, footer='hell'), 'B  Hell', A),
], True)

# 3) Schallbögen-Motiv (Desktop-Hero + Unterseiten-Kopf)
sheet('3_motiv.png', 'Frage 3 – Schallbögen aus dem Logo als Motiv', [
    label(shot('motiv_mit_s', '', 1280, 700), 'A  Mit Schallbögen (jetzt) – Startseite', B),
    label(shot('motiv_ohne_s', '', 1280, 700, motiv='ohne'), 'B  Ohne – Startseite', A),
    label(shot('motiv_mit_l', 'leistungen', 1280, 620), 'A  Mit Schallbögen (jetzt) – Unterseite', B),
    label(shot('motiv_ohne_l', 'leistungen', 1280, 620, motiv='ohne'), 'B  Ohne – Unterseite', A),
], False)

# 4) Köpfe der Unterseiten (Handy nebeneinander)
sheet('4_koepfe_handy.png', 'Frage 4 – Köpfe der Unterseiten', [
    label(shot('koepfe_rot_m', 'leistungen', 375, 812), 'A  Rot (jetzt)', B),
    label(shot('koepfe_sand_m', 'leistungen', 375, 812, koepfe='sand'), 'B  Sand', A),
    label(shot('koepfe_rot_m2', 'hoersysteme', 375, 812), 'A  Rot (jetzt)', B),
    label(shot('koepfe_sand_m2', 'hoersysteme', 375, 812, koepfe='sand'), 'B  Sand', A),
], True)

# 5) Hero am Handy
sheet('5_hero_handy.png', 'Frage 5 – Startseite am Handy', [
    label(shot('mh_sand', '', 375, 1100), 'A  Sand (jetzt)', B),
    label(shot('mh_schwarz', '', 375, 1100, mobilhero='schwarz'), 'B  Schwarz', A),
], True)
