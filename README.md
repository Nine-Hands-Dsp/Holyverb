# Holyverb — NINE HANDS | DSP

Pédale de reverb VST3 au format pédale simple, inspirée de la TC Electronic Hall of Fame : huit reverbs, de la petite
pièce de studio jusqu'à la cathédrale. Le son direct passe intact, seule la reverb est ajoutée.
Coque graphite gravée d'une cathédrale dorée, pièces photo (potards, inverseurs, footswitch, embases jack),
LED bleue qui éclaire la façade et respire avec la reverb.

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Holyverb/releases/latest/download/Holyverb-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Holyverb/releases/latest/download/Holyverb-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Holyverb/releases/latest/download/Holyverb-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-a68145?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Holyverb/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Holyverb?label=derni%C3%A8re%20version&color=a68145"></a>
</p>

## Installation

- **Windows** : dézipper `Holyverb-VST3-Windows.zip` et copier `Holyverb.vst3` dans `C:\Program Files\Common Files\VST3\`.
- **macOS** : dézipper `Holyverb-VST3-macOS.zip` et copier `Holyverb.vst3` dans `~/Library/Audio/Plug-Ins/VST3/`
  (binaire universel Apple Silicon / Intel). Le plugin n'est pas notarié : au premier lancement, dans le Terminal :
  ```
  xattr -dr com.apple.quarantine ~/Library/Audio/Plug-Ins/VST3/Holyverb.vst3
  ```
- Puis relancer le scan des plugins dans le DAW (Reaper : Préférences > Plug-ins > VST > Re-scan).

## Commandes

| Commande | Rôle |
|---|---|
| **DECAY** | Durée de la queue de reverb (plage propre à chaque mode) |
| **TONE** | Couleur de la reverb, du sombre au brillant |
| **LEVEL** | Quantité de reverb : 0 = muette, midi ≈ −6 dB, max ≈ +6 dB |
| **MODE** | Church, Plate, Hall, Room, Shimmer, Lofi, Mod, Spring |
| **PRE DELAY** | Inverseur : LONG en haut, SHORT en bas |
| **TAILS** | Inverseur : TAILS en haut (la queue continue en bypass), CUT en bas |
| **Footswitch** | Effet actif / bypass |
| **Expression** | Paramètre sans bouton pour une pédale d'expression MIDI (effet selon le mode) |

- Barre de presets et ligne d'état dans la même pastille : 14 presets d'usine, 9 presets utilisateur, valeur en direct pendant un réglage.
- MIDI Learn au clic droit sur chaque commande, aucun CC assigné par défaut ; footswitch MIDI à accrochage ou momentané.
- Fenêtre : 60 % à l'ouverture (taille minimale), 75 % ou 100 % au clic droit > *Plugin size*, jusqu'à 150 % par le coin.

Tout le détail est dans la **notice PDF** (bouton ci-dessus).

## Compilation

Le workflow GitHub Actions compile le VST3 Windows et macOS à chaque push et publie la Release.
En local : CMake ≥ 3.22 et Visual Studio 2022 (ou Xcode) ; JUCE 8.0.15 est téléchargé automatiquement.

```
cmake -B build
cmake --build build --config Release
```
