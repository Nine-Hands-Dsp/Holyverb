# HOLYVERB (Studio Wiga) - notice PDF bilingue (anglais puis francais).
# Usage : python3 tools/manual.py <fichier PDF de sortie>
# Version lue dans CMakeLists.txt. Illustrations : tools/manual_assets/ (captures reprises de la notice v1.4.0,
# toujours justes : facade de la pedale et ligne d'etat). Moteur de mise en page : tools/manual_lib.py.
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manual_lib as L

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = re.search(r"project\s*\(\s*\w+\s+VERSION\s+([0-9.]+)", open(os.path.join(ROOT, "CMakeLists.txt")).read()).group(1)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "Holyverb_Manual_EN-FR_v" + VERSION + ".pdf")

# presets usine (PluginProcessor.cpp) : nom, mode, decay, tone, level, pre-delay long
MODES = ["CHURCH", "PLATE", "HALL", "ROOM", "SHIMMER", "LOFI", "MOD", "SPRING"]
FACTORY = [("Concert Hall", 2, .50, .50, .50, 0), ("Studio Room", 3, .35, .55, .45, 0), ("Tight Ambience", 3, .10, .70, .35, 0),
           ("Vintage Plate", 1, .50, .60, .50, 0), ("Dark Plate", 1, .75, .20, .50, 1), ("Surf Spring", 7, .55, .65, .60, 0),
           ("Drippy Spring", 7, .85, .80, .70, 0), ("Cathedral", 0, .70, .40, .55, 1), ("Endless Church", 0, 1.0, .35, .60, 1),
           ("Chorus Hall", 6, .60, .55, .50, 0), ("Lofi Tape Room", 5, .45, .40, .55, 0), ("Heaven Shimmer", 4, .65, .60, .55, 1),
           ("Ambient Wash", 4, .90, .45, .70, 1), ("Huge Long Hall", 2, .90, .45, .55, 1)]

TEXTS = {"en": dict(lang="ENGLISH", sub=["Stereo reverb, 8 modes", "VST3 for Windows and macOS"], ver="User manual \u00b7 version " + VERSION),
         "fr": dict(lang="FRANÇAIS", sub=["Reverb stéréo 8 modes", "VST3 pour Windows et macOS"], ver="Notice d'utilisation \u00b7 version " + VERSION)}


def content(lang):
    en = lang == "en"
    def t(a, b): return a if en else b
    pc = lambda v: f"{round(v * 100)} %"
    b = []
    # 1. Introduction
    b += [("h1", t("1. Introduction", "1. Présentation")),
          ("p", t("<b>Holyverb</b> is a reverb pedal in VST3 form for guitar and bass, inspired by the <b>TC Electronic Hall of Fame</b>, the compact reverb with a rotary selector. Eight reverb types, from a small studio room to a cathedral, with three knobs, a selector and two mini toggles, just like a real compact pedal.",
                  "<b>Holyverb</b> est une pédale de reverb au format VST3 pour guitare et basse, inspirée de la <b>TC Electronic Hall of Fame</b>, la reverb compacte à sélecteur rotatif. Huit types de reverb, du petit studio jusqu'à la cathédrale, avec trois potards, un sélecteur et deux mini-switches, comme sur une vraie pédale compacte.")),
          ("p", t("<b>The dry signal is never touched</b>: Holyverb adds the reverb on top of your direct sound, computed in parallel. LEVEL sets the amount of effect, not the overall volume. Signal path: IN &gt; PRE DELAY &gt; reverb (MODE, DECAY) &gt; TONE &gt; LEVEL &gt; added to the dry signal &gt; OUT; the footswitch and TAILS decide what happens when you switch off.",
                  "<b>Le son direct n'est jamais touché</b> : Holyverb ajoute la reverb, calculée en parallèle, par-dessus le son direct. LEVEL règle la quantité d'effet, pas le volume général. Trajet du signal : IN &gt; PRE DELAY &gt; reverb (MODE, DECAY) &gt; TONE &gt; LEVEL &gt; ajoutée au son direct &gt; OUT ; le footswitch et TAILS décident de ce qui se passe à la coupure.")),
          ("p", t("Holyverb <b>accepts MIDI</b>: every control can be learned on a MIDI CC with a right-click (section 6), including the footswitch and the Expression parameter. No CC is assigned by default.",
                  "Holyverb <b>accepte le MIDI</b> : chaque commande s'apprend sur un CC MIDI par clic droit (section 6), y compris le footswitch et le paramètre Expression. Aucun CC n'est assigné par défaut."))]
    # 2. Installation
    b += [("h1", "2. Installation"),
          ("h2", "Windows"),
          ("p", t("Download the <b>Holyverb-VST3-Windows</b> artifact (GitHub Actions), unzip it and copy <b>Holyverb.vst3</b> into <b>C:\\Program Files\\Common Files\\VST3\\</b>.",
                  "Téléchargez l'artefact <b>Holyverb-VST3-Windows</b> (GitHub Actions), décompressez-le et copiez <b>Holyverb.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3\\</b>.")),
          ("h2", "macOS"),
          ("p", t("Download <b>Holyverb-VST3-macOS</b> (universal: Apple Silicon and Intel, macOS 10.13+), unzip it (it contains another zip), unzip again and copy <b>Holyverb.vst3</b> into <b>~/Library/Audio/Plug-Ins/VST3/</b>. The plugin is not notarized: run once in Terminal <b>xattr -dr com.apple.quarantine ~/Library/Audio/Plug-Ins/VST3/Holyverb.vst3</b>",
                  "Téléchargez <b>Holyverb-VST3-macOS</b> (universel : Apple Silicon et Intel, macOS 10.13+), décompressez-le (il contient un autre zip), décompressez encore et copiez <b>Holyverb.vst3</b> dans <b>~/Library/Audio/Plug-Ins/VST3/</b>. Le plugin n'est pas notarié : lancez une fois dans le Terminal <b>xattr -dr com.apple.quarantine ~/Library/Audio/Plug-Ins/VST3/Holyverb.vst3</b>")),
          ("h2", "Reaper"),
          ("p", t("Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Holyverb is listed by <b>Studio Wiga</b>. To use MIDI, the track must send MIDI to the plugin: record-arm it with your MIDI controller as input (or use a MIDI send from a MIDI track).",
                  "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Holyverb apparaît chez <b>Studio Wiga</b>. Pour le MIDI, la piste doit envoyer le MIDI au plugin : armez-la avec votre contrôleur MIDI en entrée (ou utilisez un envoi MIDI depuis une piste MIDI).")),
          ("pb",)]
    # 3. Overview
    rows = [["#", t("Control", "Commande"), t("Role", "Rôle")],
            ["1", "DECAY", t("Length of the reverb tail", "Durée de la queue de reverb")],
            ["2", "TONE", t("Reverb colour, dark to bright", "Couleur de la reverb, sombre à brillante")],
            ["3", "LEVEL", t("Amount of reverb added to the dry signal", "Quantité de reverb ajoutée au son direct")],
            ["4", "MODE", t("One of the 8 reverb types", "Un des 8 types de reverb")],
            ["5", "PRE DELAY (LONG / SHORT)", t("Time before the reverb comes in", "Temps avant l'arrivée de la reverb")],
            ["6", "TAILS (TAILS / CUT)", t("Tail kept or cut when bypassed", "Queue conservée ou coupée en bypass")],
            ["7", "LED", t("Lit when on, breathes with the reverb", "Allumée quand l'effet est actif, respire avec la reverb")],
            ["8", t("Status line", "Ligne d'état"), t("Mode, value of the control being moved, preset, MIDI Learn", "Mode, valeur de la commande qui bouge, preset, MIDI Learn")],
            ["9", "Footswitch", t("Effect on / bypass", "Effet actif / bypass")],
            ["10", "IN", t("Input (mono or stereo)", "Entrée (mono ou stéréo)")],
            ["11", "OUT", t("Stereo output", "Sortie stéréo")]]
    b += [("h1", t("3. Interface overview", "3. Vue d'ensemble de l'interface")),
          ("side", "annotated.png", 74, [("table", rows, [8, 30, None], {"total": 95}),
                                        ("space", 3),
                                        ("p", t("Knobs: click and drag up or right; double-click DECAY, TONE or LEVEL to return to noon. Toggles and footswitch: one click to flip. <b>Right-click a control</b> for its MIDI Learn (section 6); right-click anywhere for the full menu.",
                                                "Potards : cliquer et tirer vers le haut ou la droite ; double-clic sur DECAY, TONE ou LEVEL pour revenir à midi. Mini-switches et footswitch : un clic pour basculer. <b>Clic droit sur une commande</b> : son MIDI Learn (section 6) ; clic droit n'importe où : le menu complet."))]),
          ("pb",)]
    # 4. Controls
    b += [("h1", t("4. The controls one by one", "4. Les commandes une par une")),
          ("img", "knobs.png", 100, None),
          ("h2", "DECAY"),
          ("p", t("Length of the reverb tail. The range depends on the mode: from 0.25 s (ROOM at minimum) up to 15 s (SHIMMER at maximum), 20 s with the expression pedal. Default noon.",
                  "Durée de la queue de reverb. La plage dépend du mode : de 0,25 s (ROOM au minimum) jusqu'à 15 s (SHIMMER au maximum), 20 s avec la pédale d'expression. Défaut midi.")),
          ("h2", "TONE"),
          ("p", t("Left: dark, soft reverb. Right: bright and airy. It also sets how quickly the highs fade inside the reverb. Default noon.",
                  "À gauche : reverb sombre et douce. À droite : brillante et aérée. Règle aussi la vitesse à laquelle les aigus s'éteignent dans la reverb. Défaut midi.")),
          ("h2", "LEVEL"),
          ("p", t("Amount of reverb. MIN: silent. Noon: reverb about 6 dB below the dry sound. MAX: about 6 dB above it. Default noon.",
                  "Quantité de reverb. MIN : muette. Midi : reverb environ 6 dB sous le son direct. MAX : environ 6 dB au-dessus. Défaut midi.")),
          ("side", "mode.png", 40, [("h2", "MODE"), ("p", t("8-position stepped selector, clockwise: CHURCH, PLATE, HALL, ROOM, SHIMMER, LOFI, MOD, SPRING. Switching never clicks: the old reverb fades out before the new one starts. The status line shows the mode (“MODE HALL”). Default HALL.",
                                                            "Sélecteur cranté à 8 positions, dans le sens horaire : CHURCH, PLATE, HALL, ROOM, SHIMMER, LOFI, MOD, SPRING. Le changement ne claque jamais : l'ancienne reverb s'efface avant que la nouvelle démarre. La ligne d'état affiche le mode (« MODE HALL »). Défaut HALL."))]),
          ("side", "predelay.png", 15, [("h2", "PRE DELAY"), ("p", t("<b>LONG</b>: the reverb starts slightly after the note (25 to 120 ms depending on the mode), so the attack stays clear and fast playing articulate. <b>SHORT</b>: the reverb sticks to the note, more natural. Default SHORT.",
                                                                     "<b>LONG</b> : la reverb démarre un peu après la note (25 à 120 ms selon le mode), l'attaque reste nette et le jeu rapide articulé. <b>SHORT</b> : la reverb colle à la note, plus naturel. Défaut SHORT."))]),
          ("side", "tails.png", 15, [("h2", "TAILS"), ("p", t("<b>TAILS</b> (up): when you switch the pedal off, the reverb rings out naturally. <b>CUT</b> (down): the reverb stops as soon as the pedal is off. Default TAILS.",
                                                              "<b>TAILS</b> (haut) : quand on coupe la pédale, la reverb s'éteint naturellement. <b>CUT</b> (bas) : la reverb s'arrête dès que la pédale est coupée. Défaut TAILS."))]),
          ("side", "footswitch.png", 22, [("h2", t("Footswitch, LED and status line", "Footswitch, LED et ligne d'état")),
                                          ("p", t("One click turns the effect on or off. The blue LED is lit when the effect is on and its glow follows the reverb; in bypass it goes dark and the status line reads BYPASS. The status line shows the mode; when a control moves (mouse, automation or MIDI) it shows its value for 2.5 s, and the preset name when one is loaded.",
                                                  "Un clic active ou coupe l'effet. La LED bleue est allumée quand l'effet est actif et sa lueur suit la reverb ; en bypass elle s'éteint et la ligne d'état affiche BYPASS. La ligne d'état affiche le mode ; quand une commande bouge (souris, automation ou MIDI), elle affiche sa valeur pendant 2,5 s, et le nom du preset quand un preset est chargé."))]),
          ("pb",)]
    modes = [["Mode", t("Character", "Caractère"), t("Decay range", "Plage Decay"), t("Pre-delay S/L", "Pré-délai S/L"), t("Expression pedal", "Pédale d'expression")],
             ["CHURCH", t("Huge stone nave, very long and dark. Pads and sustained chords.", "Immense nef de pierre, très longue et sombre. Nappes et accords tenus."), "2.5 – 12 s", "25 / 120 ms", t("Longer tail, up to 20 s", "Queue plus longue, jusqu'à 20 s")],
             ["PLATE", t("Studio plate: dense, bright, no distinct echoes. Leads and vocals.", "Plaque de studio : dense, brillante, sans échos distincts. Solos et voix."), "0.6 – 7 s", "5 / 70 ms", t("Raises LEVEL to max", "Monte LEVEL au max")],
             ["HALL", t("Concert hall, wide and balanced. The all-rounder.", "Salle de concert, large et équilibrée. La polyvalente."), "0.8 – 6 s", "10 / 80 ms", t("Raises LEVEL to max", "Monte LEVEL au max")],
             ["ROOM", t("Studio room with early reflections: air without drowning your playing.", "Pièce de studio avec réflexions précoces : de l'air sans noyer le jeu."), "0.25 – 2.2 s", "2 / 40 ms", t("Raises LEVEL to max", "Monte LEVEL au max")],
             ["SHIMMER", t("Heavenly reverb: the upper octave rises in the tail. Airy soundscapes.", "Reverb céleste : l'octave supérieure monte dans la queue. Paysages aériens."), "1.5 – 15 s", "15 / 90 ms", t("More octave, tail up to 20 s", "Plus d'octave, queue jusqu'à 20 s")],
             ["LOFI", t("“Cassette” reverb: narrow band, digital grit, dirty vintage sound.", "Reverb « cassette » : bande étroite, grain numérique, vintage sale."), "0.6 – 6 s", "8 / 60 ms", t("Longer tail, up to 20 s", "Queue plus longue, jusqu'à 20 s")],
             ["MOD", t("Modulated hall that gently wavers, chorus feel in the tail.", "Hall modulé qui ondule doucement, effet chorus dans la queue."), "0.8 – 8 s", "12 / 80 ms", t("Deeper modulation, longer tail", "Modulation plus profonde, queue plus longue")],
             ["SPRING", t("Vintage amp spring with its metallic “boing”. Surf and rockabilly.", "Ressort d'ampli vintage avec son « boing » métallique. Surf et rockabilly."), "0.6 – 4.5 s", "0 / 50 ms", t("Raises LEVEL to max", "Monte LEVEL au max")]]
    if not en:
        for r in modes[1:]: r[2] = r[2].replace(".", ",")
    b += [("h2", t("The 8 modes", "Les 8 modes")),
          ("table", modes, [20, None, 24, 24, 34], {"small": True}),
          ("h2", t("Starting points", "Points de départ")),
          ("bullets", [t("<b>Rhythm</b>: ROOM or PLATE, DECAY around 10 o'clock, LEVEL around 10 o'clock, PRE DELAY SHORT.", "<b>Rythmique</b> : ROOM ou PLATE, DECAY vers 10 h, LEVEL vers 10 h, PRE DELAY SHORT."),
                       t("<b>Lead</b>: HALL or PLATE, DECAY at noon, PRE DELAY LONG to keep note attacks clear.", "<b>Solo</b> : HALL ou PLATE, DECAY à midi, PRE DELAY LONG pour garder l'attaque des notes."),
                       t("<b>Ambient</b>: SHIMMER or CHURCH, DECAY at 3 o'clock, TONE at noon, LEVEL at 2 o'clock.", "<b>Ambiance</b> : SHIMMER ou CHURCH, DECAY à 15 h, TONE à midi, LEVEL à 14 h."),
                       t("<b>Vintage</b>: SPRING, DECAY at noon, TONE around 2 o'clock to bring out the spring.", "<b>Vintage</b> : SPRING, DECAY à midi, TONE vers 14 h pour faire ressortir le ressort.")]),
          ("h1", t("5. Expression pedal", "5. Pédale d'expression")),
          ("p", t("Holyverb has an automatable <b>Expression</b> parameter, with no knob on the panel, meant for an expression pedal. What it does depends on the mode (see the table above): in ROOM, HALL, SPRING and PLATE it raises the reverb amount from the LEVEL setting up to maximum; in CHURCH and LOFI it stretches the tail up to 20 s; in MOD it deepens the modulation and lengthens the tail; in SHIMMER it adds octave and stretches the tail up to 20 s.",
                  "Holyverb a un paramètre automatisable <b>Expression</b>, sans bouton sur la façade, destiné à une pédale d'expression. Son action dépend du mode (voir le tableau ci-dessus) : en ROOM, HALL, SPRING et PLATE il monte la quantité de reverb du réglage LEVEL jusqu'au maximum ; en CHURCH et LOFI il allonge la queue jusqu'à 20 s ; en MOD il approfondit la modulation et allonge la queue ; en SHIMMER il ajoute de l'octave et allonge la queue jusqu'à 20 s.")),
          ("p", t("<b>Reverb volume under your foot</b>: in ROOM, HALL, SPRING or PLATE, set LEVEL to minimum: the reverb is silent with the pedal up and fades in as you push it down.",
                  "<b>Volume de reverb au pied</b> : en ROOM, HALL, SPRING ou PLATE, mettez LEVEL au minimum : la reverb est muette pédale levée et monte quand on l'enfonce.")),
          ("p", t("<b>Assigning the pedal</b>: right-click an empty area &gt; <b>MIDI</b> &gt; <b>Learn: Expression</b>, then move the pedal (section 6). Right-click &gt; <b>Reset expression</b> puts it back to 0. You can also link it in Reaper with Param &gt; Parameter modulation / MIDI link.",
                  "<b>Affecter la pédale</b> : clic droit sur une zone vide &gt; <b>MIDI</b> &gt; <b>Learn: Expression</b>, puis bougez la pédale (section 6). Clic droit &gt; <b>Reset expression</b> la remet à 0. On peut aussi la lier dans Reaper avec Param &gt; Parameter modulation / MIDI link.")),
          ("pb",)]
    # 6. MIDI
    learn = [[t("Control", "Commande"), "Type"],
             ["Decay, Tone, Level", t("Continuous (0–127 = MIN to MAX)", "Continu (0–127 = MIN à MAX)")],
             ["Mode", t("Selector, 8 positions: 0–127 split in 8 equal zones, in the clockwise order CHURCH, PLATE, HALL, ROOM, SHIMMER, LOFI, MOD, SPRING",
                        "Sélecteur 8 positions : 0–127 découpé en 8 zones égales, dans l'ordre horaire CHURCH, PLATE, HALL, ROOM, SHIMMER, LOFI, MOD, SPRING")],
             ["Pre-delay", t("Toggle: ≥ 64 = LONG, &lt; 64 = SHORT", "Bascule : ≥ 64 = LONG, &lt; 64 = SHORT")],
             ["Tails", t("Toggle: ≥ 64 = TAILS, &lt; 64 = CUT", "Bascule : ≥ 64 = TAILS, &lt; 64 = CUT")],
             ["Footswitch", t("Footswitch: latching (≥ 64 = on, &lt; 64 = bypass) or momentary (each press toggles)", "Footswitch : à accrochage (≥ 64 = actif, &lt; 64 = bypass) ou momentané (chaque appui bascule)")],
             ["Expression", t("Continuous (expression pedal, section 5); MIDI menu only", "Continu (pédale d'expression, section 5) ; uniquement dans le menu MIDI")]]
    b += [("h1", "6. MIDI"),
          ("p", t("Holyverb <b>accepts MIDI</b> (Control Change, any channel). <b>No CC is assigned by default</b>: everything goes through <b>MIDI Learn</b>. Assignments are <b>saved with the project</b>. Holyverb has never had factory CC numbers: a project made with an earlier version opens with its own assignments, or with none if it was made before MIDI Learn existed.",
                  "Holyverb <b>accepte le MIDI</b> (Control Change, tous canaux). <b>Aucun CC n'est assigné par défaut</b> : tout passe par le <b>MIDI Learn</b>. Les assignations sont <b>sauvegardées avec le projet</b>. Holyverb n'a jamais eu de numéros de CC d'usine : un projet fait avec une version précédente s'ouvre avec ses propres assignations, ou sans aucune s'il date d'avant le MIDI Learn.")),
          ("h2", "MIDI Learn"),
          ("bullets", [t("<b>Right-click a control</b>: DECAY, TONE, LEVEL, MODE, PRE DELAY, TAILS or the footswitch. The top of the menu shows <b>MIDI Learn: &lt;Name&gt; (CC n / none)</b>, <b>Clear MIDI: &lt;Name&gt;</b> and, while waiting, <b>Cancel MIDI learn</b> (choosing the same Learn again also cancels).",
                         "<b>Clic droit sur une commande</b> : DECAY, TONE, LEVEL, MODE, PRE DELAY, TAILS ou le footswitch. Le haut du menu affiche <b>MIDI Learn: &lt;Nom&gt; (CC n / none)</b>, <b>Clear MIDI: &lt;Nom&gt;</b> et, pendant l'attente, <b>Cancel MIDI learn</b> (choisir de nouveau le même Learn annule aussi)."),
                       t("Move a pedal, knob or footswitch on your controller: the status line shows <b>MIDI LEARN: move a control for &lt;Name&gt;</b>, then <b>&lt;Name&gt; = CC n</b> for two seconds. The learning CC does not change the sound.",
                         "Bougez une pédale, un potard ou un footswitch du contrôleur : la ligne d'état affiche <b>MIDI LEARN: move a control for &lt;Nom&gt;</b>, puis <b>&lt;Nom&gt; = CC n</b> pendant deux secondes. Le CC d'apprentissage ne modifie pas le son."),
                       t("<b>Right-click an empty area &gt; MIDI</b>: <b>Learn</b> for each control (plus <b>Expression</b>) with its current CC, <b>Cancel MIDI learn</b>, <b>Reset MIDI to defaults (no CC assigned)</b>, which clears every assignment, and the footswitch behaviour: <b>MIDI footswitch latching (127 = on / 0 = off)</b> (default) or <b>MIDI footswitch momentary (toggle each press)</b>.",
                         "<b>Clic droit sur une zone vide &gt; MIDI</b> : <b>Learn</b> pour chaque commande (plus <b>Expression</b>) avec son CC actuel, <b>Cancel MIDI learn</b>, <b>Reset MIDI to defaults (no CC assigned)</b>, qui efface toutes les assignations, et le comportement du footswitch : <b>MIDI footswitch latching (127 = on / 0 = off)</b> (par défaut) ou <b>MIDI footswitch momentary (toggle each press)</b>."),
                       t("A CC drives only one control: learning a CC already used removes it from the other control. CC 120–127 are never learned. Moving a control by MIDI unloads the preset name, like moving it with the mouse.",
                         "Un CC ne pilote qu'une commande : apprendre un CC déjà utilisé le retire de l'autre commande. Les CC 120 à 127 ne sont jamais appris. Bouger une commande en MIDI décharge le nom du preset, comme à la souris.")]),
          ("img", "status_learn.png", 120, t("MIDI Learn waiting for a CC", "MIDI Learn en attente d'un CC")),
          ("img", "status_assigned.png", 120, t("Assignment confirmed (2 s), here on an example CC", "Assignation confirmée (2 s), ici sur un CC pris en exemple")),
          ("keep", [("h2", t("Learnable controls", "Commandes apprenables")), ("table", learn, [38, None])]),
          ("bullets", [t("Holyverb does not use Program Change; the 14 factory presets are in the DAW preset menu.", "Holyverb n'utilise pas le Program Change ; les 14 presets usine sont dans le menu de presets du DAW."),
                       t("Automatable parameters: Decay, Tone, Level, Mode, Pre-Delay, Expression, On, Tails.", "Paramètres automatisables : Decay, Tone, Level, Mode, Pre-Delay, Expression, On, Tails."),
                       t("MIDI values are queued and handed to the host by a timer, never from the audio thread (anti-freeze).", "Les valeurs MIDI sont mises en file et transmises à l'hôte par un timer, jamais depuis le thread audio (anti-gel).")]),
          ("cond", 70),
          ("h1", t("7. Window", "7. Fenêtre")),
          ("p", t("Holyverb opens at the default size, <b>60 %</b> unless you choose another one, the same as Echoflex and the other single Studio Wiga pedals; the window can never be made smaller than 60 %.",
                  "Holyverb s'ouvre à la taille par défaut, <b>60 %</b> sauf si vous en choisissez une autre, comme Echoflex et les autres pédales simples Studio Wiga ; la fenêtre ne peut jamais être plus petite que 60 %.")),
          ("bullets", [t("Right-click &gt; <b>Plugin size</b>: <b>60 %</b>, <b>75 %</b> or <b>100 %</b> for this window (the current size is ticked); <b>(default)</b> is shown next to the default size you have chosen.",
                         "Clic droit &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> pour cette fenêtre (la taille actuelle est cochée) ; <b>(default)</b> est affiché à côté de la taille par défaut que vous avez choisie."),
                       t("<b>Plugin size &gt; Default size (new windows)</b>: chooses the size at which every new Holyverb window opens. This setting is common to all instances and saved on your computer (Studio Wiga\\Holyverb folder of your user data); the open window takes this size straight away.",
                         "<b>Plugin size &gt; Default size (new windows)</b> : choisit la taille d'ouverture de toutes les nouvelles fenêtres de Holyverb. Ce réglage est commun à toutes les instances et enregistré sur l'ordinateur (dossier Studio Wiga\\Holyverb des données de l'utilisateur) ; la fenêtre ouverte prend aussitôt cette taille."),
                       t("You can also drag the lower-right corner to enlarge the window up to 150 %; proportions are kept. Holyverb does not store the size of its window in the project: each time its window opens, it opens at the default size.",
                         "Vous pouvez aussi tirer le coin inférieur droit pour agrandir la fenêtre jusqu'à 150 % ; les proportions sont conservées. Holyverb n'enregistre pas de taille de fenêtre dans le projet : chaque fois que sa fenêtre s'ouvre, elle s'ouvre à la taille par défaut.")]),
          ("h2", t("Right-click menu", "Menu clic droit")),
          ("p", t("MIDI Learn of the control under the mouse (if any), then <b>Plugin size</b>, <b>Factory presets</b>, <b>Load user preset</b> / <b>Save user preset</b> (User 1 to 9), <b>Mode</b>, <b>Pre-delay long</b>, <b>Tails (reverb rings out)</b>, <b>Reset expression</b>, the <b>MIDI</b> sub-menu, and the version line.",
                  "MIDI Learn de la commande sous la souris (le cas échéant), puis <b>Plugin size</b>, <b>Factory presets</b>, <b>Load user preset</b> / <b>Save user preset</b> (User 1 à 9), <b>Mode</b>, <b>Pre-delay long</b>, <b>Tails (reverb rings out)</b>, <b>Reset expression</b>, le sous-menu <b>MIDI</b> et la ligne de version.")),
          ("img", "status_value.png", 120, t("Value of a control being moved", "Valeur d'une commande qui bouge")),
          ("pb",)]
    # 8. Presets
    pre = [[t("#", "N°"), "Preset", "Mode", "Decay", "Tone", "Level", t("Pre-delay", "Pré-délai")]]
    for i, (n, m, d, to, lv, pl) in enumerate(FACTORY):
        pre.append([str(i + 1), n, MODES[m], pc(d), pc(to), pc(lv), "Long" if pl else "Short"])
    b += [("h1", "8. Presets"),
          ("p", t("The 14 factory presets appear in the DAW preset menu (in Reaper, the list at the top of the FX window) and in the right-click menu (<b>Factory presets</b>). The loaded preset is shown on the status line (for example “P1 CONCERT HALL”).",
                  "Les 14 presets usine apparaissent dans le menu de presets du DAW (dans Reaper, la liste en haut de la fenêtre FX) et dans le menu clic droit (<b>Factory presets</b>). Le preset chargé s'affiche sur la ligne d'état (par exemple « P1 CONCERT HALL »).")),
          ("table", pre, [10, None, 26, 20, 20, 20, 22]),
          ("small", t("Values in % of knob travel. TAILS is on for every preset.", "Valeurs en % de la course des potards. TAILS est actif sur tous les presets.")),
          ("p", t("<b>Your own presets</b>: right-click &gt; <b>Save user preset</b> &gt; User 1 to 9; recall with <b>Load user preset</b>. Stored in %APPDATA%\\Studio Wiga\\Holyverb\\ (Windows) or ~/Library/Studio Wiga/Holyverb/ (macOS). The current settings are also saved with your project.",
                  "<b>Vos presets</b> : clic droit &gt; <b>Save user preset</b> &gt; User 1 à 9 ; rappel avec <b>Load user preset</b>. Stockés dans %APPDATA%\\Studio Wiga\\Holyverb\\ (Windows) ou ~/Library/Studio Wiga/Holyverb/ (macOS). Les réglages en cours sont aussi enregistrés avec le projet.")),
          ("h1", t("9. Tips", "9. Conseils d'utilisation")),
          ("bullets", [t("In Reaper, put Holyverb <b>after your amp simulator</b> (Two Notes Genome for example) for a wide, clean studio reverb: recommended. Before the amp simulator you get the rawer “pedal into the amp” sound, best kept for clean tones or SPRING.",
                         "Dans Reaper, placez Holyverb <b>après le simulateur d'ampli</b> (Two Notes Genome par exemple) pour une reverb studio large et propre : recommandé. Avant le simulateur, on obtient le son plus brut « pédale dans l'ampli », à réserver aux sons clairs ou à SPRING."),
                       t("<b>7-string and low tunings</b>: the long modes (CHURCH, SHIMMER, HALL) can thicken the low end. Turn TONE down or set PRE DELAY to LONG to keep riffs readable; SPRING naturally removes more lows than the other modes.",
                         "<b>7 cordes et accordages graves</b> : les modes longs (CHURCH, SHIMMER, HALL) peuvent épaissir le grave. Baissez TONE ou mettez PRE DELAY sur LONG pour garder les riffs lisibles ; SPRING retire naturellement plus de graves que les autres modes."),
                       t("<b>Shimmer pad under your foot</b>: SHIMMER, DECAY at 2 o'clock, TONE at noon, LEVEL at 1 o'clock, PRE DELAY LONG, TAILS on, expression pedal learned on Expression. Pedal up: a subtle shimmer; pushed down: the octave grows and the tail stretches to 20 s.",
                         "<b>Nappe shimmer au pied</b> : SHIMMER, DECAY à 14 h, TONE à midi, LEVEL à 13 h, PRE DELAY LONG, TAILS actif, pédale d'expression apprise sur Expression. Pédale levée : un léger scintillement ; enfoncée : l'octave grandit et la queue s'étire jusqu'à 20 s."),
                       t("Assign the footswitch to a MIDI foot controller and MODE to a multi-position switch or a knob to change reverb types hands-free.",
                         "Affectez le footswitch à un pédalier MIDI et MODE à un sélecteur ou un potard pour changer de reverb sans les mains.")]),
          ("keep", [("h2", t("Troubleshooting", "Dépannage")),
                    ("table", [[t("Problem", "Problème"), "Solution"],
                               [t("No reverb", "Pas de reverb"), t("LED lit? LEVEL above MIN? In ROOM / HALL / SPRING / PLATE with LEVEL at MIN, the reverb only comes in with the expression pedal.", "LED allumée ? LEVEL au-dessus de MIN ? En ROOM / HALL / SPRING / PLATE avec LEVEL au MIN, la reverb n'arrive qu'avec la pédale d'expression.")],
                               [t("The MIDI controller does nothing", "Le contrôleur MIDI ne fait rien"), t("No CC is assigned by default: learn one first (section 6). Check that the DAW sends MIDI to the plugin (armed track or MIDI send) and watch the status line.", "Aucun CC n'est assigné par défaut : apprenez-en un d'abord (section 6). Vérifiez que le DAW envoie le MIDI au plugin (piste armée ou envoi MIDI) et regardez la ligne d'état.")],
                               [t("The MIDI footswitch needs two presses", "Le footswitch MIDI demande deux appuis"), t("Choose “MIDI footswitch momentary (toggle each press)” in the MIDI sub-menu.", "Choisissez « MIDI footswitch momentary (toggle each press) » dans le sous-menu MIDI.")],
                               [t("The reverb keeps ringing after bypass", "La reverb sonne encore après le bypass"), t("TAILS is up: flip it to CUT.", "TAILS est en haut : basculez sur CUT.")],
                               [t("macOS will not load it", "macOS ne charge pas le plugin"), t("Run the xattr command (section 2), then rescan.", "Lancez la commande xattr (section 2), puis rescannez.")]],
                     [52, None])]),
          ("keep", [("h1", t("10. Technical specifications", "10. Caractéristiques techniques")),
                    ("table", [["Format", t("VST3, Windows 10/11 (64-bit) and macOS 10.13 or later (universal); MIDI input", "VST3, Windows 10/11 (64 bits) et macOS 10.13 ou plus récent (universel) ; entrée MIDI")],
                               [t("Inputs / outputs", "Entrées / sorties"), t("Mono &gt; stereo, or stereo &gt; stereo; dry signal untouched", "Mono &gt; stéréo, ou stéréo &gt; stéréo ; son direct intact")],
                               [t("Latency", "Latence"), t("None", "Aucune")],
                               [t("Engine", "Moteur"), t("8-line FDN (Hadamard) for Room, Hall, Church, Lofi, Mod, Shimmer; Dattorro plate; two simulated springs; Lofi at about 11 kHz; Shimmer with octave in the feedback loop", "FDN à 8 lignes (Hadamard) pour Room, Hall, Church, Lofi, Mod, Shimmer ; plaque de Dattorro ; deux ressorts simulés ; Lofi vers 11 kHz ; Shimmer avec octave dans la boucle")],
                               [t("Maximum tail", "Queue maximale"), t("20 seconds (CHURCH, LOFI, SHIMMER with expression fully down)", "20 secondes (CHURCH, LOFI, SHIMMER, expression à fond)")],
                               [t("Parameters", "Paramètres"), t("Decay, Tone, Level, Mode, Pre-Delay, Expression, On, Tails (all automatable)", "Decay, Tone, Level, Mode, Pre-Delay, Expression, On, Tails (tous automatisables)")],
                               ["MIDI", t("MIDI Learn on 8 controls (CC), no CC assigned by default, latching or momentary footswitch, assignments saved with the project", "MIDI Learn sur 8 commandes (CC), aucun CC assigné par défaut, footswitch à accrochage ou momentané, assignations sauvegardées avec le projet")],
                               ["Presets", t("14 factory, 9 user slots", "14 usine, 9 emplacements utilisateur")],
                               [t("Window", "Fenêtre"), t("Plugin size 60 % / 75 % / 100 %, default size of new windows selectable (60 % at first), never smaller than 60 %, up to 150 % by the corner; proportions kept", "Plugin size 60 % / 75 % / 100 %, taille par défaut des nouvelles fenêtres au choix (60 % au départ), jamais moins de 60 %, jusqu'à 150 % par le coin ; proportions conservées")],
                               [t("Stability", "Stabilité"), t("Windows anti-freeze v2: software renderer, caches rebuilt by the timer, redraw watchdog, no host call from the audio thread", "Anti-gel v2 sous Windows : rendu logiciel, caches refaits par le timer, chien de garde du redessin, aucun appel à l'hôte depuis le thread audio")],
                               ["Version", VERSION]],
                     [34, None], {"header": False})])]
    return b


L.build(OUT, "Holyverb", VERSION, "#3E6FE0", "H O L Y V E R B", TEXTS, content)
