# HOLYVERB (NINE HANDS | DSP) - notice PDF en francais, illustree avec le rendu reel du plugin (tools/render).
# Usage : python3 tools/manual.py <dossier des captures (tools/render)> <fichier PDF de sortie>
import os, sys, json, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import svgr
SHOTS = sys.argv[1]
OUT = sys.argv[2]
VERSION = "1.6.0"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_notice_tmp"); os.makedirs(TMP, exist_ok=True)
FONTS = os.path.join(ROOT, "assets", "fonts")
for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("Title", "BarlowCondensed-ExtraBold")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))

ACC = colors.HexColor("#A68145"); ACC_L = colors.HexColor("#D9B574")      # or de la cathedrale
DARK = colors.HexColor("#1E1C19"); GREY = colors.HexColor("#6A665F"); LIGHT = colors.HexColor("#F3EEE4")
LAY = json.load(open(os.path.join(ROOT, "tools", "layout.json")))
LOGO_PNG = os.path.join(TMP, "nine_hands_logo_blanc.png")
Image.fromarray(svgr.render(os.path.join(ROOT, "NineHandsLogo.svg"), 1200)).save(LOGO_PNG)

# ------------------------------------------------------------------ images
def shot(name): return Image.open(os.path.join(SHOTS, name)).convert("RGB")
src = shot("holy_status.png")                       # fenetre 100 % (958 px) capturee en 2x
k = src.height / 900.0                              # repere du plugin : 617,5 x 900 unites
kn, tg = LAY["knobs"], LAY["toggles"]
BAR = LAY["preset"]
marks = [(1, kn[0][0] - 64, kn[0][1] - 70), (2, kn[1][0] - 64, kn[1][1] - 70), (3, kn[2][0] + 64, kn[2][1] - 70),
         (4, LAY["mode"][0] + 4, LAY["mode"][1] + 84), (5, tg[0][0] + 44, tg[0][1] + 6), (6, tg[1][0] - 44, tg[1][1] + 6),
         (7, LAY["led"][0] + 30, LAY["led"][1]), (8, BAR[0] - 20, BAR[1] + 19), (9, LAY["fs"][0] + 72, LAY["fs"][1]),
         (10, 586, LAY["jackY"] - 48), (11, 32, LAY["jackY"] - 48)]
ann = src.copy(); dr = ImageDraw.Draw(ann)
fnt = ImageFont.truetype(os.path.join(FONTS, "Poppins-Bold.ttf"), 34)
for n, x, y in marks:
    cx, cy, r = x * k, y * k, 27
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=(166, 129, 69), width=5)
    dr.text((cx, cy + 1), str(n), font=fnt, fill=(30, 28, 25), anchor="mm")
annotated = os.path.join(TMP, "annotated.jpg"); ann.save(annotated, quality=90)

def crop_u(im, box, kk): return im.crop(tuple(int(v * kk) for v in box))
gap = 18
def strip(parts, path):
    s = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), max(p.height for p in parts)), (255, 255, 255))
    x = 0
    for p in parts: s.paste(p, (x, 0)); x += p.width + gap
    s.save(path, quality=90); return path

kx = 1800 / 900.0                                   # captures exactes 1235 x 1800
ex_sh, ex_hall, ex_by = shot("holy_exact.png"), shot("holy_exact_hall.png"), shot("holy_exact_bypass.png")
# potards
knobs_img = strip([crop_u(ex_hall, (40, 60, 578, 240), kx)], os.path.join(TMP, "knobs.jpg"))
# selecteur MODE : Hall puis Shimmer
mx, my = LAY["mode"][0], LAY["mode"][1]
box_m = (mx - 150, my - 108, mx + 150, my + 92)
mode_img = strip([crop_u(ex_hall, box_m, kx), crop_u(ex_sh, box_m, kx)], os.path.join(TMP, "mode.jpg"))
# inverseurs : Concert Hall (SHORT en bas, TAILS en haut) puis Heaven Shimmer (LONG en haut)
box_l = (tg[0][0] - 60, tg[0][1] - 104, tg[0][0] + 60, tg[0][1] + 72)
box_r = (tg[1][0] - 60, tg[1][1] - 104, tg[1][0] + 60, tg[1][1] + 72)
sw_img = strip([crop_u(ex_hall, box_l, kx), crop_u(ex_sh, box_l, kx), crop_u(ex_hall, box_r, kx)], os.path.join(TMP, "switches.jpg"))
# LED : bypass / actif
box_on = (LAY["led"][0] - 90, LAY["led"][1] - 30, LAY["led"][0] + 90, LAY["led"][1] + 30)
on_img = strip([crop_u(ex_by, box_on, kx), crop_u(ex_hall, box_on, kx)], os.path.join(TMP, "onoff.jpg"))
# pastille : barre de presets au repos / ligne d'etat
box_bar = (BAR[0] - 8, BAR[1] - 8, BAR[0] + BAR[2] + 8, BAR[1] + BAR[3] + 8)
bar_img = strip([crop_u(shot("holy_bypass.png"), box_bar, k), crop_u(src, box_bar, k)], os.path.join(TMP, "bar.jpg"))

# couverture : pedale detouree (canal alpha de background.png), reflet au sol, halo or tres doux
cutsrc = ex_sh
bg_a = Image.open(os.path.join(ROOT, "background.png")).split()[3].resize(cutsrc.size, Image.LANCZOS)
cut = Image.new("RGBA", cutsrc.size, (0, 0, 0, 0)); cut.paste(cutsrc, (0, 0), bg_a)
cut = cut.crop(cut.getbbox())
cw, ch = cut.size
pad = int(cw * 0.16)
canvas = Image.new("RGBA", (cw + 2 * pad, int(ch * 1.30) + pad), (0, 0, 0, 255))
yy, xx = np.mgrid[0:canvas.height, 0:canvas.width].astype(np.float64)
gcx, gcy = canvas.width / 2, pad + ch * 0.45
glow = np.exp(-(((xx - gcx) / (cw * 0.62)) ** 2 + ((yy - gcy) / (ch * 0.48)) ** 2)) * 30
edge = np.clip(np.minimum.reduce([xx, canvas.width - 1 - xx, yy, canvas.height - 1 - yy]) / (pad * 0.9), 0, 1)
glow *= edge ** 2
halo = np.dstack([glow * 0.95, glow * 0.75, glow * 0.40, np.full_like(glow, 255)]).astype(np.uint8)
canvas = Image.alpha_composite(canvas, Image.fromarray(halo, "RGBA"))
refl = cut.transpose(Image.FLIP_TOP_BOTTOM)
ra = np.array(refl).astype(np.float64)
fade = np.clip(1 - np.arange(refl.height) / (refl.height * 0.22), 0, 1) ** 1.6 * 0.22
ra[..., 3] *= fade[:, None]
canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA"), (pad, pad + ch + 6))
canvas.alpha_composite(cut, (pad, pad))
canvas = canvas.crop((0, 0, canvas.width, pad + int(ch * 1.20)))
cover = os.path.join(TMP, "cover.jpg"); canvas.convert("RGB").save(cover, quality=92)
ASSETS = os.path.join(ROOT, "tools", "manual_assets")
shutil.rmtree(ASSETS, ignore_errors=True); os.makedirs(ASSETS)
for p in (annotated, knobs_img, mode_img, sw_img, on_img, bar_img, cover): shutil.copy(p, ASSETS)

def img(path, width):
    im = Image.open(path); h = width * im.height / im.width
    return RLImage(path, width=width, height=h)

# ------------------------------------------------------------------ styles
st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=20, leading=24, textColor=ACC, spaceAfter=8, spaceBefore=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=13, leading=17, textColor=DARK, spaceAfter=4, spaceBefore=10, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=5),
    "tip": ParagraphStyle("tip", fontName="Pop", fontSize=9.0, leading=12.4, textColor=DARK, spaceAfter=3),
    "small": ParagraphStyle("small", fontName="Pop", fontSize=8.2, leading=11.5, textColor=GREY),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.4, leading=11, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.4, leading=11, textColor=DARK),
    "cells": ParagraphStyle("cells", fontName="Pop", fontSize=7.8, leading=10, textColor=DARK),
    "cellbs": ParagraphStyle("cellbs", fontName="PopM", fontSize=7.8, leading=10, textColor=DARK),
}
def P(t, s="p"): return Paragraph(t, st[s])
def bullets(items, s="p"): return [P("&bull;&nbsp;&nbsp;" + i, s) for i in items]
def table(rows, widths, header=True, small=False):
    data = [[P(c, ("cellbs" if small else "cellb") if (header and r == 0) else ("cells" if small else "cell")) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E2DACB")),
             ("TOPPADDING", (0, 0), (-1, -1), 2 if small else 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 2 if small else 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC)]
    t.setStyle(TableStyle(style)); return t

# ------------------------------------------------------------------ donnees (identiques au code livre)
MODES = [  # mode, caractere, decay min -> max, pre-delay short / long, expression
    ("CHURCH", "Immense nef de pierre, très longue et sombre. Pour les nappes et les accords tenus.", "2,5 à 12 s", "25 / 120 ms", "allonge la queue jusqu'à 20 s"),
    ("PLATE", "Plaque de studio : dense, brillante, sans écho distinct. Idéale pour le lead et le chant.", "0,6 à 7 s", "5 / 70 ms", "monte LEVEL jusqu'au maximum"),
    ("HALL", "Salle de concert, ample et équilibrée : le réglage polyvalent.", "0,8 à 6 s", "10 / 80 ms", "monte LEVEL jusqu'au maximum"),
    ("ROOM", "Pièce de studio avec premières réflexions : de l'air sans noyer le jeu.", "0,25 à 2,2 s", "2 / 40 ms", "monte LEVEL jusqu'au maximum"),
    ("SHIMMER", "Reverb céleste : l'octave supérieure monte dans la queue.", "1,5 à 15 s", "15 / 90 ms", "plus d'octave, queue jusqu'à 20 s"),
    ("LOFI", "Reverb « cassette » : bande étroite, grain numérique, son vintage.", "0,6 à 6 s", "8 / 60 ms", "allonge la queue jusqu'à 20 s"),
    ("MOD", "Hall modulé qui ondule doucement, effet chorus dans la queue.", "0,8 à 8 s", "12 / 80 ms", "modulation plus profonde, queue plus longue"),
    ("SPRING", "Ressort d'ampli vintage et son « boing » métallique : surf, rockabilly.", "0,6 à 4,5 s", "0 / 50 ms", "monte LEVEL jusqu'au maximum")]
FACTORY = [  # nom, mode, decay, tone, level, pre long, description
    ("Concert Hall", "HALL", 50, 50, 50, 0, "La salle de concert à mi-course : le point de départ polyvalent."),
    ("Studio Room", "ROOM", 35, 55, 45, 0, "Une pièce naturelle, pour aérer une rythmique sans l'éloigner."),
    ("Tight Ambience", "ROOM", 10, 70, 35, 0, "Ambiance très courte et claire : épaissit le son sans queue audible."),
    ("Vintage Plate", "PLATE", 50, 60, 50, 0, "La plaque de studio classique, brillante, pour le lead."),
    ("Dark Plate", "PLATE", 75, 20, 50, 1, "Plaque longue et sombre, pré-délai long : l'attaque reste devant."),
    ("Surf Spring", "SPRING", 55, 65, 60, 0, "Le ressort surf, bien présent."),
    ("Drippy Spring", "SPRING", 85, 80, 70, 0, "Ressort long et brillant : le « dégoulinant » des amplis vintage."),
    ("Cathedral", "CHURCH", 70, 40, 55, 1, "Nef de pierre, longue et sombre."),
    ("Endless Church", "CHURCH", 100, 35, 60, 1, "La cathédrale au maximum : des nappes qui n'en finissent pas."),
    ("Chorus Hall", "MOD", 60, 55, 50, 0, "Hall modulé, effet chorus dans la queue."),
    ("Lofi Tape Room", "LOFI", 45, 40, 55, 0, "Reverb « cassette » granuleuse et étroite."),
    ("Heaven Shimmer", "SHIMMER", 65, 60, 55, 1, "Shimmer céleste, octave dans la queue."),
    ("Ambient Wash", "SHIMMER", 90, 45, 70, 1, "Nappe ambiante très longue."),
    ("Huge Long Hall", "HALL", 90, 45, 55, 1, "Grande salle, longue queue, pré-délai long.")]

W = A4[0] - 36 * mm
f = [NextPageTemplate("p"), Spacer(1, 1), PageBreak()]
f.append(P("1. Présentation", "h1"))
f += [P("<b>HOLYVERB</b> est une pédale de reverb NINE HANDS | DSP inspirée de la <b>TC Electronic Hall of Fame</b> : huit reverbs, "
        "de la petite pièce de studio jusqu'à la cathédrale, avec trois potards, un sélecteur de mode et deux inverseurs, comme sur une vraie pédale compacte."),
      P("Le <b>son direct n'est jamais touché</b> : la reverb est calculée à côté puis ajoutée par-dessus. LEVEL règle donc la quantité d'effet, pas le volume général. "
        "Les reverbs de salle (ROOM, HALL, CHURCH, LOFI, MOD, SHIMMER) reposent sur un réseau de 8 lignes à retard réinjectées, PLATE sur une plaque de type Dattorro, "
        "SPRING sur deux ressorts simulés (chaînes de filtres dispersifs), et SHIMMER transpose la queue d'une octave à chaque passage dans la boucle.")]
f.append(P("2. Installation", "h1"))
for h, x in (("Windows", "Téléchargez <b>Holyverb-VST3-Windows.zip</b> avec le bouton du README du dépôt GitHub Nine-Hands-Dsp/Holyverb (il donne toujours la dernière version), décompressez-le et copiez le dossier <b>Holyverb.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3</b>."),
             ("macOS", "Téléchargez <b>Holyverb-VST3-macOS.zip</b>, décompressez-le et copiez <b>Holyverb.vst3</b> dans <b>~/Bibliothèque/Audio/Plug-Ins/VST3</b>. Si macOS le bloque, tapez <b>xattr -dr com.apple.quarantine ~/Library/Audio/Plug-Ins/VST3/Holyverb.vst3</b> dans le Terminal. Le binaire est universel (Apple Silicon et Intel)."),
             ("Reaper", "Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Le plugin apparaît sous le nom <b>Holyverb (NINE HANDS | DSP)</b>. Pour le piloter avec des footswitchs et pédales d'expression MIDI, la piste doit recevoir le MIDI du contrôleur (armement ou monitoring d'entrée, entrée MIDI réglée sur votre appareil, par exemple la M-Vave Chocolate Plus).")):
    f.append(P(h, "h2")); f.append(P(x))
f.append(PageBreak())
f.append(P("3. Vue d'ensemble de l'interface", "h1"))
ov_rows = [["#", "Commande", "Rôle"],
   ["1", "DECAY", "Durée de la queue de reverb. Glisser vers le haut / le bas, molette, double-clic = midi, clic droit = MIDI Learn (valable pour toutes les commandes)."],
   ["2", "TONE", "Couleur de la reverb : sombre à gauche, brillante à droite."],
   ["3", "LEVEL", "Quantité de reverb ajoutée au son direct."],
   ["4", "MODE", "Sélecteur des 8 reverbs."],
   ["5", "Inverseur PRE DELAY", "En haut = LONG, en bas = SHORT."],
   ["6", "Inverseur TAILS", "En haut = TAILS (la queue continue en bypass), en bas = CUT."],
   ["7", "LED", "Bleue = effet actif, sa lueur suit la reverb ; éteinte = bypass."],
   ["8", "Barre de presets / ligne d'état", "Au repos : flèches = preset précédent / suivant, clic sur le nom = menu des presets. Pendant un réglage : valeur en direct."],
   ["9", "Footswitch", "Effet actif / bypass."],
   ["10", "IN", "Jack d'entrée (mono ou stéréo)."],
   ["11", "OUT", "Jack de sortie (stéréo)."]]
ov = Table([[[img(annotated, 86 * mm), Spacer(1, 4 * mm), img(on_img, 60 * mm), P("LED : bypass, puis effet actif (la façade reçoit la lumière bleue).", "small")],
             table(ov_rows, [8 * mm, 27 * mm, W - 90 * mm - 35 * mm])]], colWidths=[90 * mm, W - 90 * mm])
ov.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
f.append(ov); f.append(PageBreak())
f.append(P("4. Les commandes en détail", "h1"))
f.append(KeepTogether([img(knobs_img, W * 0.80), Spacer(1, 2 * mm)]))
for h, x in (("DECAY", "Durée de la queue de reverb. La plage dépend du mode (voir le tableau des modes) : de 0,25 s (ROOM au minimum) jusqu'à 15 s (SHIMMER au maximum)."),
             ("TONE", "À gauche, une reverb sombre et feutrée ; à droite, brillante et aérée. TONE agit aussi sur l'absorption des aigus à l'intérieur de la reverb : plus il est bas, plus les aigus meurent vite dans la queue."),
             ("LEVEL", "Quantité de reverb : <b>MIN</b> = muette, <b>midi</b> = reverb 6 dB sous le son direct, <b>MAX</b> = reverb 6 dB au-dessus. Un limiteur doux évite les crêtes trop fortes.")):
    f.append(P(h, "h2")); f.append(P(x))
f.append(P("MODE", "h2"))
f.append(P("Sélecteur à 8 positions crantées, dans le sens des aiguilles d'une montre : CHURCH, PLATE, HALL, ROOM, SHIMMER, LOFI, MOD, SPRING. "
           "Le changement se fait sans clic : l'ancienne reverb s'éteint en douceur avant que la nouvelle démarre."))
f.append(KeepTogether([img(mode_img, W * 0.62), P("Sélecteur MODE sur HALL, puis sur SHIMMER.", "small")]))
f.append(P("Inverseurs PRE DELAY et TAILS", "h2"))
f.append(P("<b>PRE DELAY</b> : en haut (<b>LONG</b>), la reverb arrive un peu après la note, l'attaque reste nette ; en bas (<b>SHORT</b>), elle colle à la note. "
           "<b>TAILS</b> : en haut (<b>TAILS</b>), quand on coupe la pédale, la reverb finit de résonner naturellement ; en bas (<b>CUT</b>), elle s'arrête net. "
           "Un clic, ou la molette, fait basculer l'inverseur."))
f.append(KeepTogether([img(sw_img, W * 0.50), P("PRE DELAY en bas (SHORT), PRE DELAY en haut (LONG), TAILS en haut.", "small")]))
f.append(P("5. Les 8 modes", "h1"))
f.append(table([["Mode", "Caractère", "DECAY", "Pré-délai S / L", "Pédale d'expression"]] + [[f"<b>{m}</b>", c, d, p, e] for m, c, d, p, e in MODES],
               [18 * mm, W - 18 * mm - 22 * mm - 22 * mm - 38 * mm, 22 * mm, 22 * mm, 38 * mm], small=True))
f.append(P("Accordages graves", "h2"))
f.append(P("Avec une 7 cordes accordée en Sol ou plus bas, les modes longs (CHURCH, SHIMMER, HALL) peuvent épaissir le bas du spectre : baissez TONE ou passez PRE DELAY sur LONG pour garder les riffs lisibles. SPRING coupe naturellement plus de graves que les autres."))
f.append(P("6. Footswitch, LED et pédale d'expression", "h1"))
f += bullets(["<b>Footswitch</b> : il bascule dès l'appui et le bouton s'assombrit tant qu'on appuie. En bypass, avec TAILS en haut, la reverb en cours finit de résonner.",
              "<b>LED</b> : bleue quand l'effet est actif, la façade autour reçoit sa lumière ; sa lueur respire avec la reverb. Elle s'allume et s'éteint en fondu.",
              "<b>Expression</b> : paramètre sans bouton, prévu pour une pédale d'expression MIDI (MIDI Learn ou automation). Son effet dépend du mode (dernière colonne du tableau). "
              "Astuce : en ROOM, HALL, SPRING ou PLATE, LEVEL au minimum et pédale d'expression = volume de reverb au pied. Clic droit &gt; <b>Reset expression</b> la remet à zéro."])
f.append(P("7. MIDI", "h1"))
f.append(P("Toutes les commandes se pilotent depuis un contrôleur MIDI (footswitchs, pédales d'expression, potards). Holyverb écoute tous les canaux MIDI. "
           "<b>Aucun CC n'est assigné d'office</b> : vous choisissez chacun avec le <b>MIDI Learn</b>."))
f.append(KeepTogether([table([["Commande", "Assignation", "Type"],
    ["Decay, Tone, Level", "MIDI Learn", "Continu (0-127 = toute la course)"], ["Mode", "MIDI Learn", "8 zones égales sur 0-127"],
    ["Pre-delay, Tails", "MIDI Learn", "Bascule : 64 ou plus = en haut"],
    ["Footswitch", "MIDI Learn", "À accrochage (127 = on / 0 = off) ou momentané (bascule à chaque appui), clic droit &gt; Settings"],
    ["Expression", "MIDI Learn", "Continu"]], [36 * mm, 26 * mm, W - 62 * mm])]))
f.append(Spacer(1, 2 * mm))
f += bullets(["<b>MIDI Learn</b> : clic droit sur une commande &gt; <b>MIDI Learn: &lt;nom&gt;</b>, puis bougez la pédale ou appuyez sur le bouton MIDI. La ligne d'état affiche <b>MIDI LEARN  Decay</b>, puis confirme pendant 2 secondes, par ex. <b>Decay = CC 64</b>. Un CC déjà utilisé par une autre commande passe à la nouvelle. <b>Clear MIDI</b> retire une assignation ; clic droit &gt; MIDI &gt; <b>Clear all MIDI assignments</b> les retire toutes. L'Expression s'apprend depuis clic droit &gt; MIDI.",
              "Tous les paramètres sont aussi automatisables dans le DAW."])
f.append(P("8. Fenêtre, presets et ligne d'état", "h1"))
f.append(P("Holyverb utilise le format pédale simple : la fenêtre s'ouvre à <b>60 %</b> et ne peut jamais être réduite en dessous. Clic droit &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> ; "
           "<b>Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres. Le coin en bas à droite agrandit la fenêtre jusqu'à 150 %, proportions conservées. Tous les menus s'ouvrent là où vous cliquez."))
wt = Table([[[P("La <b>barre de presets</b> et la <b>ligne d'état</b> partagent la même pastille. Au repos, elle affiche le preset en cours (ou <i>Edited</i>) et l'état du bypass. "
                "Dès qu'un réglage bouge (souris, molette, automation, MIDI), la ligne d'état prend sa place avec la valeur en direct (ex. <i>Decay 64 %</i>, <i>Mode Hall</i>) et les messages du MIDI Learn ; "
                "elle s'efface 2,5 s après le dernier mouvement. Un clic sur la pastille fait revenir la barre de presets tout de suite.")],
             [img(bar_img, 66 * mm), P("Au repos (presets), puis pendant un réglage.", "small")]]], colWidths=[W - 70 * mm, 70 * mm])
wt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0)]))
f.append(wt)
f.append(P("Presets", "h2"))
f.append(P("Flèches de la barre, clic sur son nom, clic droit n'importe où, ou menu de presets du DAW (les 14 presets d'usine y apparaissent). Clic droit &gt; <b>Save user preset</b> enregistre jusqu'à 9 presets personnels ; les réglages en cours sont aussi sauvegardés avec le projet."))
rows = [["#", "Preset", "Mode", "Decay · Tone · Level (%)", "Pré-délai", "Description"]]
for i, (n, m, d, t_, l, pl, ds) in enumerate(FACTORY):
    rows.append([str(i + 1), f"<b>{n}</b>", m, f"{d} · {t_} · {l}", "Long" if pl else "Short", ds])
f.append(table(rows, [7 * mm, 26 * mm, 17 * mm, 26 * mm, 14 * mm, W - 90 * mm], small=True))
f.append(P("TAILS est en haut sur tous les presets d'usine.", "small"))
f.append(P("9. Conseils d'utilisation", "h1"))
f += bullets(["Dans Reaper, placez Holyverb <b>après</b> votre simulateur d'ampli (Ampire puis Impulse pour le baffle) pour une reverb « studio » large et propre ; <b>avant</b> l'ampli, elle sonne comme une pédale branchée dans l'ampli, plus brute.",
              "<b>Rythmique</b> : ROOM ou PLATE, DECAY vers 10 h, LEVEL vers 10 h, PRE DELAY SHORT. <b>Lead</b> : HALL ou PLATE, DECAY à midi, PRE DELAY LONG.",
              "<b>Ambiance</b> : SHIMMER ou CHURCH, DECAY à 15 h, TONE à midi, LEVEL à 14 h, avec la pédale d'expression pour faire monter la nappe.",
              "<b>Vintage</b> : SPRING, DECAY à midi, TONE vers 14 h pour faire ressortir le ressort."], "tip")
f.append(KeepTogether([P("10. Caractéristiques techniques", "h1"), table([
    ["Format", "VST3 (Windows 64 bits, macOS universel)"], ["Canaux", "Mono à stéréo ou stéréo à stéréo"], ["Latence", "Aucune"],
    ["Modes", "Church, Plate, Hall, Room, Shimmer, Lofi, Mod, Spring"], ["Queue maximale", "20 s (Church, Lofi, Shimmer avec l'expression à fond)"],
    ["Paramètres", "Decay, Tone, Level, Mode, Pre-Delay, Expression, On, Tails (tous automatisables)"],
    ["MIDI", "tous les canaux ; MIDI Learn sur les 8 commandes (rien d'assigné par défaut)"],
    ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, jusqu'à 150 %, jamais sous 60 % ; anti-gel v2 sous Windows"]],
    [30 * mm, W - 30 * mm], header=False, small=True)]))

def deco(c, doc):
    c.saveState()
    c.setFillColor(DARK); c.rect(0, A4[1] - 6 * mm, A4[0], 6 * mm, stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 6.8 * mm, A4[0], 0.8 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, "Holyverb (NINE HANDS | DSP) · v" + VERSION)
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="HOLYVERB - Notice v" + VERSION, author="NINE HANDS | DSP")
# ---- Couverture « minimale » (gabarit fixe commun a toutes les notices) ----
COVER_NAME = "HOLYVERB"; COVER_SUB = "Reverb 8 modes"
PEDAL_H, PEDAL_MAXW, PEDAL_TOP = 82 * mm, 115 * mm, 84 * mm
LANG_TOP = 18 * mm
NAME_TOP, NAME_PT = 194 * mm, 30
SUB_TOP, SUB_PT = 208 * mm, 10
LOGO_W, LOGO_BOTTOM = 38 * mm, 22 * mm
BAND_H = 3 * mm
def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, 0, A4[0], BAND_H, stroke=0, fill=1)
    def line(text, top, font, size, cs, col):
        w = pdfmetrics.stringWidth(text, font, size) + cs * (len(text) - 1)
        t = c.beginText((A4[0] - w) / 2, A4[1] - top - size * 0.8); t.setFont(font, size); t.setCharSpace(cs)
        t.setFillColor(col); t.textOut(text); c.drawText(t)
    line("FRANÇAIS", LANG_TOP, "PopM", 8.5, 0, ACC_L)
    ci = Image.open(cover); iw, ih = ci.size
    cw = iw / 1.32; ch = (ih - int(cw * 0.16)) / 1.2; pad = int(cw * 0.16)
    kk = min(PEDAL_H / ch, PEDAL_MAXW / cw)
    dw, dh = iw * kk, ih * kk
    y0 = A4[1] - (PEDAL_TOP + (PEDAL_H - ch * kk) / 2) + pad * kk
    c.drawImage(cover, (A4[0] - dw) / 2, y0 - dh, dw, dh)
    line(COVER_NAME, NAME_TOP - NAME_PT * 0.02, "Title", NAME_PT, NAME_PT * 0.5, colors.white)
    line(COVER_SUB, SUB_TOP, "Pop", SUB_PT, 1.5, colors.HexColor("#BDC4B8"))
    lw, lh = Image.open(LOGO_PNG).size
    c.drawImage(LOGO_PNG, (A4[0] - LOGO_W) / 2, LOGO_BOTTOM, LOGO_W, LOGO_W * lh / lw, mask="auto")
    c.restoreState()
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
doc.build(f)
shutil.rmtree(TMP, ignore_errors=True)
print(OUT)
