"""
HOLYVERB (NINE HANDS | DSP) - visuel du plugin v2 (nov. 2026), entierement synthetise : pedale simple 1235 x 1800 px.

Refonte aux regles NINE HANDS | DSP :
  - coque peinte graphite chaud (couleur de la coque du visuel d'origine), grain metallise fin ;
  - cathedrale vectorielle de l'utilisateur (design/source/cathedrale.svg, or #a68145) imprimee sur la coque,
    sous tous les elements (reserves autour des potards, inverseurs, textes, LED, barre, footswitch, logo, vis) ;
  - pieces photo du kit (assets/kit) : potards, inverseurs haut / milieu / bas, LED, footswitch, embases jack, vis d'angle ;
  - textes, graduations et logo NINE HANDS | DSP dessines en vectoriel par le plugin (Layout.h), jamais dans le fond.
Une seule lumiere pour toute la pedale : en haut a gauche (ombres portees vers le bas a droite).

Sorties (racine du depot) : background.png, glow_blue.png, led_on.png, fs_refl.png, toggle_strip.png,
Layout.h, tools/layout.json, design/preview_art.png (fond seul).
Usage : python3 tools/make_art.py
"""
import os, sys, math, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import photo_controls as PC
import toggle_photo as TP
import svgr

AS = 2
UW, UH = 760, 958
W, H = UW * AS, UH * AS
L = np.array([-0.46, -0.62, 0.64]); L /= np.linalg.norm(L)
V = np.array([0.0, 0.0, 1.0]); HV = (L + V) / np.linalg.norm(L + V)

# ------------------------------------------------------------------ geometrie (unites de travail)
OUT_W, OUT_H = 1235, 1800
JACK_LEN = 104.0
_jtest = PC.jack_sprite(JACK_LEN, AS, 1)
JACK_PROT = _jtest[1] - 1.5 / AS
PY0, PH, PR = 34.0, 890.0, 30.0
PW = OUT_W / OUT_H * PH - 2 * JACK_PROT
PX0 = (UW - PW) / 2
CX = PX0 + PW / 2
CROP_X0, CROP_W = PX0 - JACK_PROT, PW + 2 * JACK_PROT
SC = (OUT_H / 2.0) / PH                           # unites de travail -> unites du plugin (617,5 x 900)

# disposition du visuel d'origine (potards en haut, selecteur au centre, inverseurs de part et d'autre, LED, titre,
# ligne d'etat, footswitch, logo), recalee sur le boitier plein cadre
KR = 58.0                                         # potards DECAY / TONE / LEVEL
KDX = 0.322 * PW
KY = 186.0
KNOBS = [(CX - KDX, KY, 'DECAY', KR), (CX, KY, 'TONE', KR), (CX + KDX, KY, 'LEVEL', KR)]
MODE = (CX, 414.0); MODE_R = 63.0
MODES = ['CHURCH', 'PLATE', 'HALL', 'ROOM', 'SHIMMER', 'LOFI', 'MOD', 'SPRING']     # sens horaire (index du parametre)
TOG_R = 23.0
TOG_S = TOG_R * 3.6
TDX = 0.352 * PW
TOGGLES = [(CX - TDX, 414.0, 'PRE DELAY', 'LONG', 'SHORT'), (CX + TDX, 414.0, 'TAILS', 'TAILS', 'CUT')]
LED = (CX, 548.0); LED_LENS = 10.5
TITLE_Y = 612.0
RULE_Y = 650.0
PILL_W = 400.0 / SC; PILL_H = 38.0 / SC             # pastille de reference (Strong Pickle) : 400 x 38 unites du plugin
PRESET = (CX - PILL_W / 2, 672.0, PILL_W, PILL_H)
STATUS = PRESET
FS = (CX, 796.0); FS_FLATS = 100.0
LOGO_C, LOGO_W = (CX, 892.0), 196.0
JACK_Y = 512.0
SCREW_R = 9.5; SCREW_IN = 21.0
SCREWS = [(PX0 + SCREW_IN, PY0 + SCREW_IN, 12.0), (PX0 + PW - SCREW_IN, PY0 + SCREW_IN, 57.0),
          (PX0 + SCREW_IN, PY0 + PH - SCREW_IN, 101.0), (PX0 + PW - SCREW_IN, PY0 + PH - SCREW_IN, 33.0)]

# ------------------------------------------------------------------ outils
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
UX, UY = (XX + 0.5) / AS, (YY + 0.5) / AS

def rrect_sd(x, y, x0, y0, w, h, r):
    cx, cy = x0 + w / 2, y0 + h / 2
    qx = np.abs(x - cx) - (w / 2 - r); qy = np.abs(y - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

def fbm(shape, scales, amps, seed=0):
    r = np.random.default_rng(seed); out = np.zeros(shape, np.float32)
    for s, a in zip(scales, amps):
        n = r.standard_normal((max(2, shape[0] // s + 2), max(2, shape[1] // s + 2))).astype(np.float32)
        out += a * cv2.resize(n, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)
    return out

def over(dst, rgba, x0, y0):
    h, w = rgba.shape[:2]
    X0, Y0 = int(round(x0)), int(round(y0))
    sx0, sy0 = max(0, -X0), max(0, -Y0)
    ex, ey = min(w, dst.shape[1] - X0), min(h, dst.shape[0] - Y0)
    a = rgba[sy0:ey, sx0:ex, 3:4] / 255.0
    reg = dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex]
    dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex] = reg * (1 - a) + rgba[sy0:ey, sx0:ex, :3] * a

# ------------------------------------------------------------------ 1. coque : peinture graphite chaud metallisee (couleur du visuel d'origine)
sd = rrect_sd(UX, UY, PX0, PY0, PW, PH, PR)
body = np.clip(0.5 - sd * AS, 0, 1)
EDGE = 9.0
d_in = np.clip(-sd, 0, None)
hgt = np.where(d_in < EDGE, np.sqrt(np.clip(EDGE ** 2 - (EDGE - d_in) ** 2, 0, None)), EDGE)
gy, gx = np.gradient(cv2.GaussianBlur(hgt, (0, 0), 1.0), 1.0 / AS)
nrm = np.dstack([-gx, -gy, np.ones_like(hgt)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
ndl = np.clip(nrm @ L, 0, 1); ndh = np.clip(nrm @ HV, 0, 1)
paint = np.array([76.0, 72.0, 66.0])                       # graphite chaud (coque du visuel Holyverb d'origine)
encl = paint * (0.55 + 0.70 * ndl)[..., None] + (58 * ndh ** 40 + 15 * ndh ** 6)[..., None] * np.array([1.0, 0.98, 0.95])
rng = np.random.default_rng(11)
flake = (rng.random((H, W)) ** 16).astype(np.float32)
flake = cv2.GaussianBlur(flake, (0, 0), 0.6) * 55          # paillettes discretes (grain metallise fin)
sheen = np.exp(-(((UX - 250) / 330) ** 2 + ((UY - 230) / 380) ** 2))
grain = fbm((H, W), [1, 2], [1.5, 0.9], 3) + 0.9 * fbm((H, W), [90, 260], [0.8, 1.0], 4)
encl += grain[..., None] * np.array([1.0, 0.98, 0.94])
encl += (flake * (0.40 + 0.8 * sheen))[..., None] * np.array([1.0, 0.97, 0.92])
encl += (14.0 * sheen)[..., None] * np.array([1.0, 0.97, 0.92])
shade = 1.0 + 0.07 * np.clip(1 - (UX - PX0) / PW * 0.7 - (UY - PY0) / PH * 0.7, -1, 1)
encl *= shade[..., None]
img = encl * body[..., None]

# ------------------------------------------------------------------ 2. serigraphie (vectorielle dans le plugin) : textes, graduations
SS = 2; K = AS * SS; KW, KH = W * SS, H * SS
FONT = {'medium': os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Medium.ttf'),
        'bold': os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Bold.ttf'),
        'light': os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Light.ttf')}
ink_im = Image.new('L', (KW, KH), 0); dr = ImageDraw.Draw(ink_im)
VTEXT, VTICKS = [], []
def font(kind, em): return ImageFont.truetype(FONT[kind], max(4, int(round(em * K))))
def text(x, y, txt, kind, em, track, anchor='m'):
    f = font(kind, em)
    widths = [f.getlength(ch) for ch in txt]
    total = sum(widths) + track * K * (len(txt) - 1)
    cx = x * K - total / 2 if anchor == 'm' else (x * K if anchor == 'l' else x * K - total)
    VTEXT.append((txt, kind, em, track, (cx + total / 2) / K, y, 0))
    for ch, w in zip(txt, widths):
        dr.text((cx, y * K), ch, font=f, fill=255, anchor='lm'); cx += w + track * K
    return total / K
LAB_EM, LAB_TR = 19.0, 2.4
SMALL_EM, SMALL_TR = 12.5, 1.4
for (x, y, name, R) in KNOBS:
    text(x, y - R - 25.0, name, 'medium', LAB_EM, LAB_TR)
    a0 = math.radians(-135)
    text(x + (R + 4) * math.sin(a0) + 2, y - (R + 4) * math.cos(a0) + 14, 'MIN', 'medium', SMALL_EM, SMALL_TR)
    text(x - (R + 4) * math.sin(a0) - 2, y - (R + 4) * math.cos(a0) + 14, 'MAX', 'medium', SMALL_EM, SMALL_TR)
    for i in range(11):                                   # graduations : 11 traits de 7 h 30 a 4 h 30, tous de meme taille
        a = math.radians(-135 + 27 * i)
        r0, r1 = R * 1.10, R * 1.21
        VTICKS.append((x + r0 * math.sin(a), y - r0 * math.cos(a), x + r1 * math.sin(a), y - r1 * math.cos(a), 1.7))
        dr.line([((x + r0 * math.sin(a)) * K, (y - r0 * math.cos(a)) * K), ((x + r1 * math.sin(a)) * K, (y - r1 * math.cos(a)) * K)], fill=255, width=int(1.7 * K))
# selecteur MODE : 8 crans de 7 h 30 a 4 h 30
MODE_ANG = [-135 + 270 * i / 7 for i in range(8)]
for name, ang in zip(MODES, MODE_ANG):
    a = math.radians(ang)
    r0, r1 = MODE_R * 1.10, MODE_R * 1.27
    VTICKS.append((MODE[0] + r0 * math.sin(a), MODE[1] - r0 * math.cos(a), MODE[0] + r1 * math.sin(a), MODE[1] - r1 * math.cos(a), 2.0))
    dr.line([((MODE[0] + r0 * math.sin(a)) * K, (MODE[1] - r0 * math.cos(a)) * K), ((MODE[0] + r1 * math.sin(a)) * K, (MODE[1] - r1 * math.cos(a)) * K)], fill=255, width=int(2.0 * K))
    rl = MODE_R * 1.40
    lx, ly = MODE[0] + rl * math.sin(a), MODE[1] - rl * math.cos(a)
    f = font('medium', 14.5)
    tw = sum(f.getlength(c) for c in name) / K + 1.6 * (len(name) - 1)
    s = math.sin(a)
    lx += s * (tw / 2 + 2)                                # le texte s'ecarte du cran selon son cote
    ly += -math.cos(a) * 8
    text(lx, ly, name, 'medium', 14.5, 1.6)
for (x, y, name, up, dn) in TOGGLES:
    if name != up:
        text(x, y - TOG_R * 3.30, name, 'medium', LAB_EM - 1.5, LAB_TR)      # nom de la commande : grand (demande, nov. 2026)
    text(x, y - TOG_R * 2.25, up, 'medium', SMALL_EM + 1.5, 1.8)          # positions : petit
    text(x, y + TOG_R * 2.35, dn, 'medium', SMALL_EM + 1.5, 1.8)
TITLE_W = text(CX, TITLE_Y, 'HOLYVERB', 'bold', 56.0, 3.0)
RULES = [(CX - TITLE_W / 2, RULE_Y - 0.8, TITLE_W, 1.6)]
dr.rectangle(((CX - TITLE_W / 2) * K, (RULE_Y - 0.8) * K, (CX + TITLE_W / 2) * K, (RULE_Y + 0.8) * K), fill=255)
text(PX0 + 40.0, JACK_Y, 'OUT', 'medium', 15.0, 1.8)
text(PX0 + PW - 40.0, JACK_Y, 'IN', 'medium', 15.0, 1.8)
ink = cv2.resize(np.asarray(ink_im, np.float32) / 255.0, (W, H), interpolation=cv2.INTER_AREA)

# ------------------------------------------------------------------ 3. cathedrale (design/source/cathedrale.svg), or, sous tous les elements
print('cathedrale...')
SVG = os.path.join(ROOT, 'design', 'source', 'cathedrale.svg')
CB = (856.0, 3236.0, 88.0, 4016.0)                       # boite du dessin dans le cadre 4096 du SVG (x0, x1, y0, y1)
CATH_H = PH - 54.0                                       # hauteur du dessin (meme echelle en largeur : rien n'est etire)
k_u = CATH_H / (CB[3] - CB[2])
npx = int(round(4096 * k_u * AS))
cv_ = svgr.render(SVG, npx, npx).astype(np.float32)
c_a = cv_[..., 3] / 255.0
CATH_C = (CX, PY0 + PH / 2 + 4.0)
x0p = int(round((CATH_C[0] - (0.5 * (CB[0] + CB[1])) * k_u) * AS)); y0p = int(round((CATH_C[1] - (0.5 * (CB[2] + CB[3])) * k_u) * AS))
lay = np.zeros((H, W), np.float32)
sx0, sy0 = max(0, -x0p), max(0, -y0p); ex, ey = min(npx, W - x0p), min(npx, H - y0p)
lay[y0p + sy0:y0p + ey, x0p + sx0:x0p + ex] = c_a[sy0:ey, sx0:ex]
# reserves : chaque mot (boite + marge), potards, selecteur, inverseurs, LED, barre, footswitch, logo, vis
keep = np.zeros((H, W), np.float32)
words = cv2.morphologyEx((ink > 0.05).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 31), np.uint8))
n_, lab_, st_, _ = cv2.connectedComponentsWithStats(words, 8)
for i in range(1, n_):
    x_, y_, w_, h_, a_ = st_[i]
    if h_ < 200 and w_ > 6:
        m = 5 * AS
        keep[max(0, y_ - m):y_ + h_ + m, max(0, x_ - m):x_ + w_ + m] = 1.0
_lg = svgr.render(os.path.join(ROOT, 'NineHandsLogo.svg'), int(LOGO_W * AS))[..., 3]
_lh = _lg.shape[0]; _lw = _lg.shape[1]; _x0, _y0 = int(LOGO_C[0] * AS - _lw / 2), int(LOGO_C[1] * AS - _lh / 2)
keep[_y0 - 14:_y0 + _lh + 14, _x0 - 14:_x0 + _lw + 14] = 1.0
for (x, y, _, R) in KNOBS: keep = np.maximum(keep, (np.hypot(UX - x, UY - y) < R + 4).astype(np.float32))
keep = np.maximum(keep, (np.hypot(UX - MODE[0], UY - MODE[1]) < MODE_R * 1.30).astype(np.float32))
for t in TOGGLES: keep = np.maximum(keep, (np.hypot(UX - t[0], UY - t[1]) < TOG_R + 3).astype(np.float32))
keep = np.maximum(keep, (np.hypot(UX - LED[0], UY - LED[1]) < LED_LENS * 2.0).astype(np.float32))
keep = np.maximum(keep, (np.abs(rrect_sd(UX, UY, *PRESET, PILL_H / 2)) * 0 + (rrect_sd(UX, UY, *PRESET, PILL_H / 2) < 6)).astype(np.float32))
keep = np.maximum(keep, (np.hypot(UX - FS[0], UY - FS[1]) < FS_FLATS * 0.64).astype(np.float32))
for (x, y, _r) in SCREWS: keep = np.maximum(keep, (np.hypot(UX - x, UY - y) < SCREW_R + 4).astype(np.float32))
keep = cv2.GaussianBlur(keep, (0, 0), 0.8 * AS)
on_top = np.clip((-sd - 7.0) / 2.0, 0, 1)
cut = np.clip(keep * 1.4, 0, 1)
# petits morceaux coupes par une reserve : retires en entier plutot que tronques (pas de fragment isole)
n0, lab0, st0, _ = cv2.connectedComponentsWithStats((lay > 0.4).astype(np.uint8), 8)
keptc = np.bincount(lab0.ravel(), weights=(cut < 0.5).ravel().astype(np.float64), minlength=n0)
frac = keptc / np.maximum(st0[:, 4], 1)
drop = np.zeros(n0, bool); drop[1:] = (frac[1:] < 0.98) & (st0[1:, 4] < 600 * AS * AS / 4)
dropm = cv2.dilate(drop[lab0].astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
vis = ((lay > 0.4) & (cut < 0.5) & (dropm < 0.5)).astype(np.uint8)
n1, lab1, st1, _ = cv2.connectedComponentsWithStats(vis, 8)
tiny = np.zeros(n1, bool); tiny[1:] = (st1[1:, 4] < (10 * AS) ** 2 * 0.5) & (np.maximum(st1[1:, 2], st1[1:, 3]) < 12 * AS)
whole = np.bincount(lab0.ravel(), minlength=n0)
src_size = np.zeros(n1)
for i in np.where(tiny)[0]:
    ys_, xs_ = np.where(lab1 == i); src_size[i] = whole[lab0[ys_[0], xs_[0]]]
tiny &= src_size > st1[:, 4] * 1.6
dropm = np.maximum(dropm, cv2.dilate(tiny[lab1].astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32))
cath_a = np.clip(lay * 0.92, 0, 1) * (1 - cut) * (1 - dropm) * on_top
gold = np.array([166.0, 129.0, 69.0])                     # #a68145 (couleur du SVG)
# encre doree imprimee : un peu metallisee (plus claire dans la lumiere), grain de la peinture conserve
gr_ = img - cv2.GaussianBlur(img, (0, 0), 2.0)
light = 1.0 + 0.10 * np.clip(1 - (UX - PX0) / PW * 0.7 - (UY - PY0) / PH * 0.7, -1, 1)
glint = (flake / 55.0 * 60.0)[..., None] * np.array([1.0, 0.85, 0.55])
gold_col = gold * light[..., None] * 0.94 + 0.5 * gr_ + glint * 0.5
img = img * (1 - cath_a[..., None]) + gold_col * cath_a[..., None]
img += (fbm((H, W), [1], [0.9], 22) * body)[..., None]

# ------------------------------------------------------------------ 4. commandes (photos du kit)
print('potards, vis, inverseurs, LED, footswitch...')
def occlusion(mask, strength=1.0):
    contact = cv2.GaussianBlur(mask, (0, 0), 3.0 * AS)
    soft = cv2.GaussianBlur(mask, (0, 0), 14.0 * AS)
    o = np.clip(contact * 0.55 + soft * 0.9, 0, 0.5) * strength * (1.0 - mask)
    img[...] = img * (1.0 - o * body)[..., None]
_m = np.zeros((H, W), np.float32)
for (x, y, _, R) in KNOBS + [(MODE[0], MODE[1], '', MODE_R)]: _m = np.maximum(_m, np.clip((R - np.hypot(UX - x, UY - y)) * AS, 0, 1))
_m = np.maximum(_m, np.clip((LED_LENS * 1.07 - np.hypot(UX - LED[0], UY - LED[1])) * AS, 0, 1) * 0.6)
_fs_tmp = PC.footswitch_sprite(FS_FLATS, AS)[0]
_n = _fs_tmp.shape[0]; _x0 = int(round((FS[0] - _n / AS / 2) * AS)); _y0 = int(round((FS[1] - _n / AS / 2) * AS))
_fa = np.zeros((H, W), np.float32); _fa[_y0:_y0 + _n, _x0:_x0 + _n] = np.clip((_fs_tmp[..., 3] / 255.0 - 0.86) / 0.14, 0, 1)
_m = np.maximum(_m, _fa)
occlusion(_m)
for (x, y, _, R) in KNOBS + [(MODE[0], MODE[1], '', MODE_R)]:
    KN, KS = PC.knob_sprite(R, AS)
    over(img, KN, (x - KS / 2) * AS, (y - KS / 2) * AS)
for (x, y, rot) in SCREWS:
    SP, SS_ = PC.screw_sprite(SCREW_R, AS, rot_deg=rot)
    over(img, SP, (x - SS_ / 2) * AS, (y - SS_ / 2) * AS)
LD, LDON, LS = PC.led_sprites(LED_LENS, AS, colour='blue')
over(img, LD, (LED[0] - LS / 2) * AS, (LED[1] - LS / 2) * AS)
Image.fromarray(np.clip(LDON, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'led_on.png'))
FSPR, FSREFL, FS_W, FS_BTN = PC.footswitch_sprite(FS_FLATS, AS, refl_colour=(60.0, 140.0, 255.0))
over(img, FSPR, (FS[0] - FS_W / 2) * AS, (FS[1] - FS_W / 2) * AS)
Image.fromarray(FSREFL, 'RGBA').save(os.path.join(ROOT, 'fs_refl.png'))
TFR = TP.aligned_frames(TOG_R, TOG_S, AS * 2)              # inverseurs dessines par le plugin (4 px par unite)
Image.fromarray(np.concatenate(TFR, 0), 'RGBA').save(os.path.join(ROOT, 'toggle_strip.png'), optimize=True)
# ombre de contact de la rondelle des inverseurs sur la coque (le sprite porte deja l'ombre du levier)
_t = np.zeros((H, W), np.float32)
for t in TOGGLES: _t = np.maximum(_t, np.clip((TOG_R * 1.0 - np.hypot(UX - t[0], UY - t[1])) * AS, 0, 1))
occlusion(_t, 0.6)

# ------------------------------------------------------------------ 5. embases jack (photo du kit) : OUT a gauche, IN a droite
alpha = body.copy()
for side in (-1, 1):
    j, jw_u, jh_u = PC.jack_sprite(JACK_LEN, AS, side)
    jh, jw = j.shape[:2]
    jw2 = int(math.floor(JACK_PROT * AS))
    if jw2 != jw:
        pm_ = j.copy(); pm_[..., :3] *= pm_[..., 3:4] / 255.0
        pm_ = cv2.resize(pm_, (jw2, jh), interpolation=cv2.INTER_AREA)
        a_ = np.maximum(pm_[..., 3:4], 1e-3); pm_[..., :3] = np.where(pm_[..., 3:4] > 0.5, pm_[..., :3] * 255.0 / a_, 0)
        j = pm_; jw = jw2
    x0 = int(round((PX0 * AS - jw) if side < 0 else ((PX0 + PW) * AS)))
    y0 = int(round(JACK_Y * AS - jh / 2))
    occ = np.zeros((H, W), np.float32); occ[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
    occ = np.clip(cv2.GaussianBlur(occ, (0, 0), 3.0 * AS) * 0.9 + cv2.GaussianBlur(occ, (0, 0), 18.0 * AS) * 1.6, 0, 0.62)
    occ *= 0.2 if side > 0 else 0.0
    img *= (1.0 - occ * body)[..., None]
    over(img, j, x0, y0)
    ja = np.zeros((H, W), np.float32); ja[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
    alpha = np.maximum(alpha, ja)

# ------------------------------------------------------------------ 6. sauvegarde du fond
def to_out(a):
    x0, x1 = CROP_X0 * AS, (CROP_X0 + CROP_W) * AS
    y0, y1 = PY0 * AS, (PY0 + PH) * AS
    M = np.float32([[OUT_W / (x1 - x0), 0, -x0 * OUT_W / (x1 - x0)], [0, OUT_H / (y1 - y0), -y0 * OUT_H / (y1 - y0)]])
    return cv2.warpAffine(a, M, (OUT_W, OUT_H), flags=cv2.INTER_AREA if OUT_H < (y1 - y0) else cv2.INTER_CUBIC)
out_rgb = np.clip(to_out(img), 0, 255); out_a = np.clip(to_out(alpha), 0, 1)
Image.fromarray(np.dstack([out_rgb, out_a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'background.png'), optimize=True)

# ------------------------------------------------------------------ 7. facade eclairee par la LED bleue (calque alpha : seule la lumiere ajoutee)
GR = 110.0
def glow(c, fn, col=(0.20, 0.50, 1.0)):
    x0p, y0p = round((c[0] - GR) * AS), round((c[1] - GR) * AS)
    size = round(2 * GR * AS)
    reg = img[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.hypot((xx + 0.5) / AS - GR, (yy + 0.5) / AS - GR)
    h1, h2 = 8.0, 30.0
    E = 2.0 * h1 ** 3 / (d ** 2 + h1 ** 2) ** 1.5 + 0.30 * h2 ** 3 / (d ** 2 + h2 ** 2) ** 1.5
    E *= np.clip((GR - d) / 30.0, 0, 1)
    E[d < LED_LENS * 1.07] *= 0.0
    lum = reg.mean(2, keepdims=True)
    lit = reg + (reg * 2.6 + 20.0 * np.clip(lum / 40.0, 0.3, 1.6)) * E[..., None] * np.array(col)
    add = lit - reg
    a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
    Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, fn))
    return (x0p / AS, y0p / AS, size / AS, size / AS)
GLR = glow(LED, 'glow_blue.png')

# ------------------------------------------------------------------ 8. Layout.h (repere du plugin : 617,5 x 900 unites)
def f(v): return f"{v:.2f}f"
def X(v): return (v - CROP_X0) * SC
def Y(v): return (v - PY0) * SC
def PT(p): return "{ %s, %s }" % (f(X(p[0])), f(Y(p[1])))
def RC(r): return "{ %s, %s, %s, %s }" % (f(X(r[0])), f(Y(r[1])), f(r[2] * SC), f(r[3] * SC))
fk = {'medium': 0, 'bold': 1, 'light': 2}
json.dump({"frame": [OUT_W / 2, OUT_H / 2], "knobs": [[X(k[0]), Y(k[1]), k[3] * SC] for k in KNOBS],
           "mode": [X(MODE[0]), Y(MODE[1]), MODE_R * SC], "modeAngles": MODE_ANG,
           "toggles": [[X(t[0]), Y(t[1])] for t in TOGGLES], "togR": TOG_R * SC, "togS": TOG_S * SC,
           "led": [X(LED[0]), Y(LED[1])], "ledS": LS * SC, "glow": [X(GLR[0]), Y(GLR[1]), GLR[2] * SC, GLR[3] * SC],
           "fs": [X(FS[0]), Y(FS[1])], "fsS": FS_W * SC, "footR": FS_BTN * SC,
           "preset": [X(PRESET[0]), Y(PRESET[1]), PRESET[2] * SC, PRESET[3] * SC], "jackY": Y(JACK_Y),
           "jackL": X(PX0 - JACK_PROT / 2), "jackR": X(PX0 + PW + JACK_PROT / 2),
           "box": [X(PX0), Y(PY0), PW * SC, PH * SC], "logo": [X(LOGO_C[0]), Y(LOGO_C[1]), LOGO_W * SC],
           "texts": [[t[0], t[1], t[2] * SC, t[3] * SC, X(t[4]), Y(t[5]), t[6]] for t in VTEXT],
           "ticks": [[X(d[0]), Y(d[1]), X(d[2]), Y(d[3]), d[4] * SC] for d in VTICKS],
           "rules": [[X(r[0]), Y(r[1]), r[2] * SC, r[3] * SC] for r in RULES]},
          open(os.path.join(ROOT, 'tools', 'layout.json'), 'w'), indent=1)
with open(os.path.join(ROOT, 'Layout.h'), 'w') as fo:
    fo.write(f"// genere par tools/make_art.py - ne pas modifier a la main (repere {OUT_W / 2} x {OUT_H / 2} = fond {OUT_W} x {OUT_H} px / 2)\n#pragma once\n#include <juce_graphics/juce_graphics.h>\nnamespace layout\n{{\n")
    fo.write(f"    constexpr float frameW = {f(OUT_W / 2)}, frameH = {f(OUT_H / 2)};   // pedale plein cadre (jacks aux bords gauche / droit)\n")
    fo.write("    // ordre : decay, tone, level\n")
    fo.write("    const juce::Point<float> knobPos[3] = { " + ", ".join(PT(k[:2]) for k in KNOBS) + " };\n")
    fo.write(f"    const float knobR = {f(KR * SC)};\n")
    fo.write(f"    const juce::Point<float> modePos {PT(MODE)}; const float modeR = {f(MODE_R * SC)};\n")
    fo.write(f"    const juce::Point<float> preDelayPos {PT(TOGGLES[0][:2])}, tailsPos {PT(TOGGLES[1][:2])};\n")
    fo.write(f"    const float togS = {f(TOG_S * SC)}, togR = {f(TOG_R * SC)};   // sprite d'inverseur (cote) / rondelle\n")
    fo.write(f"    const juce::Point<float> ledPos {PT(LED)}; const float ledS = {f(LS * SC)};\n")
    fo.write(f"    const juce::Rectangle<float> glowRect {RC(GLR)};\n")
    fo.write(f"    const juce::Point<float> fsPos {PT(FS)}; const float footR = {f(FS_BTN * SC)}, fsS = {f(FS_W * SC)};   // bouton / sprite\n")
    fo.write(f"    const juce::Rectangle<float> presetRect {RC(PRESET)};   // pastille unique : presets au repos, ligne d'etat pendant les reglages\n")
    fo.write(f"    const float presetFont = 23.0f;   // Poppins Medium (reference Strong Pickle)\n")
    fo.write(f"    const juce::Rectangle<float> boxRect {RC((PX0, PY0, PW, PH))};\n")
    fo.write(f"    const float jackY = {f(Y(JACK_Y))};\n")
    fo.write("    // serigraphie vectorielle : texte, police (0 medium, 1 bold, 2 light), taille em, espacement, centre, rotation (degres)\n")
    fo.write("    struct Txt { const char* s; int font; float em, track, x, y, rot; };\n")
    fo.write("    const Txt texts[] = {\n" + ",\n".join(f'        {{ "{t[0]}", {fk[t[1]]}, {f(t[2] * SC)}, {f(t[3] * SC)}, {f(X(t[4]))}, {f(Y(t[5]))}, {f(t[6])} }}' for t in VTEXT) + "\n    };\n")
    fo.write("    struct Tick { float x0, y0, x1, y1, w; };\n")
    fo.write("    const Tick ticks[] = { " + ", ".join(f"{{ {f(X(d[0]))}, {f(Y(d[1]))}, {f(X(d[2]))}, {f(Y(d[3]))}, {f(d[4] * SC)} }}" for d in VTICKS) + " };\n")
    fo.write("    const juce::Rectangle<float> rules[] = { " + ", ".join(RC(r) for r in RULES) + " };\n")
    fo.write(f"    const juce::Point<float> logoPos {PT(LOGO_C)}; const float logoW = {f(LOGO_W * SC)};\n")
    fo.write("}\n")
print('ok', 'boitier %.1f x %.1f unites' % (PW * SC, PH * SC), 'pastille', PILL_W * SC, PILL_H * SC)
