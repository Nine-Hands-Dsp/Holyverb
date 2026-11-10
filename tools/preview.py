"""Apercu complet de la facade (ce que dessine le plugin) : fond + serigraphie vectorielle + inverseurs + reperes des
potards + LED + barre de presets + logo. Usage : python3 tools/preview.py [sortie.png] [led 0/1] [preset]"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import svgr

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'design', 'preview.png')
led_on = (sys.argv[2] != '0') if len(sys.argv) > 2 else True
preset = sys.argv[3] if len(sys.argv) > 3 else 'Concert Hall'
Lj = json.load(open(os.path.join(HERE, 'layout.json')))
S = 2.0                                                    # px par unite du plugin (image 1235 x 1800)
SS = 3                                                     # sur-echantillonnage du dessin vectoriel
bg = Image.open(os.path.join(ROOT, 'background.png')).convert('RGBA')
Wp, Hp = bg.size
canvas = Image.new('RGBA', (Wp, Hp), (14, 14, 15, 255)); canvas.alpha_composite(bg)

def paste(fn, rect):
    im = Image.open(os.path.join(ROOT, fn)).convert('RGBA')
    x, y, w, h = [v * S for v in rect]
    canvas.alpha_composite(im.resize((int(round(w)), int(round(h))), Image.LANCZOS), (int(round(x)), int(round(y))))

if led_on:
    paste('glow_blue.png', Lj['glow'])
    ls = Lj['ledS']; paste('led_on.png', (Lj['led'][0] - ls / 2, Lj['led'][1] - ls / 2, ls, ls))
    fss = Lj['fsS']; paste('fs_refl.png', (Lj['fs'][0] - fss / 2, Lj['fs'][1] - fss / 2, fss, fss))

# inverseurs : PRE DELAY en bas (SHORT), TAILS en haut
strip = Image.open(os.path.join(ROOT, 'toggle_strip.png')).convert('RGBA')
n = strip.width
frames = [strip.crop((0, i * n, n, (i + 1) * n)) for i in range(3)]
ts = Lj['togS']
for (pos, fr) in ((Lj['toggles'][0], 2), (Lj['toggles'][1], 0)):
    im = frames[fr].resize((int(round(ts * S)), int(round(ts * S))), Image.LANCZOS)
    canvas.alpha_composite(im, (int(round((pos[0] - ts / 2) * S)), int(round((pos[1] - ts / 2) * S))))

# couche vectorielle sur-echantillonnee
V = Image.new('RGBA', (Wp * SS, Hp * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(V)
INK = (242, 239, 232, 255)
K = S * SS
FONTS = {'medium': 'Poppins-Medium.ttf', 'bold': 'Poppins-Bold.ttf', 'light': 'Poppins-Light.ttf'}
for (s, kind, em, track, x, y, rot) in Lj['texts']:
    f = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', FONTS[kind]), int(round(em * K)))
    widths = [f.getlength(c) for c in s]; total = sum(widths) + track * K * (len(s) - 1)
    cx = x * K - total / 2
    for c, w in zip(s, widths):
        d.text((cx, y * K), c, font=f, fill=INK, anchor='lm'); cx += w + track * K
for (x0, y0, x1, y1, w) in Lj['ticks']:
    d.line([(x0 * K, y0 * K), (x1 * K, y1 * K)], fill=INK, width=max(1, int(round(w * K))))
for (x, y, w, h) in Lj['rules']:
    d.rectangle((x * K, y * K, (x + w) * K, (y + h) * K), fill=INK)
# reperes des potards (index blanc + point), positions : decay 11 h, tone midi, level 1 h ; mode HALL
def pointer(cx, cy, R, ang, white=True):
    a = math.radians(ang); ux, uy = math.sin(a), -math.cos(a)
    d.line([((cx + ux * R * 0.18) * K, (cy + uy * R * 0.18) * K), ((cx + ux * R * 0.62) * K, (cy + uy * R * 0.62) * K)],
           fill=(246, 246, 248, 255), width=int(R * 0.06 * K))
for (k, ang) in zip(Lj['knobs'], (-40, 0, 35)):
    pointer(k[0], k[1], k[2], ang)
mx, my, mr = Lj['mode']
pointer(mx, my, mr, Lj['modeAngles'][2])
# barre de presets (pastille de reference)
x, y, w, h = Lj['preset']
d.rounded_rectangle((x * K, y * K, (x + w) * K, (y + h) * K), radius=h / 2 * K, fill=(8, 8, 10, 215), outline=(255, 255, 255, 34), width=int(1 * K))
fp = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Medium.ttf'), int(23 * K))
d.text(((x + w / 2) * K, (y + h / 2 + 1) * K), preset, font=fp, fill=(236, 236, 240, 255), anchor='mm')
for sgn in (-1, 1):
    ax = (x + 17) if sgn < 0 else (x + w - 17); ay = y + h / 2; t = 5.5
    pts = [((ax - sgn * t * 0.6) * K, (ay - t) * K), ((ax - sgn * t * 0.6) * K, (ay + t) * K), ((ax + sgn * t * 0.9) * K, ay * K)]
    d.polygon(pts, fill=(255, 255, 255, 150))
V = V.resize((Wp, Hp), Image.LANCZOS)
canvas.alpha_composite(V)
# logo NINE HANDS | DSP
lx, ly, lw = Lj['logo']
lg = Image.fromarray(svgr.render(os.path.join(ROOT, 'NineHandsLogo.svg'), int(round(lw * S * 2))))
lg = lg.resize((int(round(lw * S)), int(round(lg.height * lw * S / lg.width))), Image.LANCZOS)
canvas.alpha_composite(lg, (int(round(lx * S - lg.width / 2)), int(round(ly * S - lg.height / 2))))
canvas.convert('RGB').save(out)
print(out)
