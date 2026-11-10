// genere par tools/make_art.py - ne pas modifier a la main (repere 617.5 x 900.0 = fond 1235 x 1800 px / 2)
#pragma once
#include <juce_graphics/juce_graphics.h>
namespace layout
{
    constexpr float frameW = 617.50f, frameH = 900.00f;   // pedale plein cadre (jacks aux bords gauche / droit)
    // ordre : decay, tone, level
    const juce::Point<float> knobPos[3] = { { 123.75f, 153.71f }, { 308.75f, 153.71f }, { 493.75f, 153.71f } };
    const float knobR = 58.65f;
    const juce::Point<float> modePos { 308.75f, 384.27f }; const float modeR = 63.71f;
    const juce::Point<float> preDelayPos { 106.52f, 384.27f }, tailsPos { 510.98f, 384.27f };
    const float togS = 83.73f, togR = 23.26f;   // sprite d'inverseur (cote) / rondelle
    const juce::Point<float> ledPos { 308.75f, 519.78f }; const float ledS = 26.54f;
    const juce::Rectangle<float> glowRect { 197.51f, 408.54f, 222.47f, 222.47f };
    const juce::Point<float> fsPos { 308.75f, 770.56f }; const float footR = 38.31f, fsS = 192.13f;   // bouton / sprite
    const juce::Rectangle<float> presetRect { 108.75f, 645.17f, 400.00f, 38.00f };   // pastille unique : presets au repos, ligne d'etat pendant les reglages
    const float presetFont = 23.0f;   // Poppins Medium (reference Strong Pickle)
    const juce::Rectangle<float> boxRect { 21.49f, 0.00f, 574.52f, 900.00f };
    const float jackY = 483.37f;
    // serigraphie vectorielle : texte, police (0 medium, 1 bold, 2 light), taille em, espacement, centre, rotation (degres)
    struct Txt { const char* s; int font; float em, track, x, y, rot; };
    const Txt texts[] = {
        { "DECAY", 0, 19.21f, 2.43f, 123.75f, 69.78f, 0.00f },
        { "MIN", 0, 12.64f, 1.42f, 81.44f, 212.20f, 0.00f },
        { "MAX", 0, 12.64f, 1.42f, 166.06f, 212.20f, 0.00f },
        { "TONE", 0, 19.21f, 2.43f, 308.75f, 69.78f, 0.00f },
        { "MIN", 0, 12.64f, 1.42f, 266.44f, 212.20f, 0.00f },
        { "MAX", 0, 12.64f, 1.42f, 351.06f, 212.20f, 0.00f },
        { "LEVEL", 0, 19.21f, 2.43f, 493.75f, 69.78f, 0.00f },
        { "MIN", 0, 12.64f, 1.42f, 451.44f, 212.20f, 0.00f },
        { "MAX", 0, 12.64f, 1.42f, 536.06f, 212.20f, 0.00f },
        { "CHURCH", 0, 14.66f, 1.62f, 219.22f, 453.06f, 0.00f },
        { "PLATE", 0, 14.66f, 1.62f, 194.32f, 395.16f, 0.00f },
        { "HALL", 0, 14.66f, 1.62f, 215.25f, 332.51f, 0.00f },
        { "ROOM", 0, 14.66f, 1.62f, 270.36f, 292.45f, 0.00f },
        { "SHIMMER", 0, 14.66f, 1.62f, 351.36f, 292.45f, 0.00f },
        { "LOFI", 0, 14.66f, 1.62f, 400.50f, 332.51f, 0.00f },
        { "MOD", 0, 14.66f, 1.62f, 418.30f, 395.16f, 0.00f },
        { "SPRING", 0, 14.66f, 1.62f, 394.71f, 453.06f, 0.00f },
        { "PRE DELAY", 0, 14.16f, 1.82f, 106.52f, 304.03f, 0.00f },
        { "LONG", 0, 17.70f, 2.43f, 106.52f, 329.61f, 0.00f },
        { "SHORT", 0, 17.70f, 2.43f, 106.52f, 441.25f, 0.00f },
        { "TAILS", 0, 17.70f, 2.43f, 510.98f, 329.61f, 0.00f },
        { "CUT", 0, 17.70f, 2.43f, 510.98f, 441.25f, 0.00f },
        { "HOLYVERB", 1, 56.63f, 3.03f, 308.75f, 584.49f, 0.00f },
        { "OUT", 0, 15.17f, 1.82f, 61.94f, 483.37f, 0.00f },
        { "IN", 0, 15.17f, 1.82f, 555.56f, 483.37f, 0.00f }
    };
    struct Tick { float x0, y0, x1, y1, w; };
    const Tick ticks[] = { { 78.13f, 199.33f, 73.57f, 203.89f, 1.72f }, { 62.39f, 173.64f, 56.26f, 175.64f, 1.72f }, { 60.03f, 143.62f, 53.66f, 142.61f, 1.72f }, { 71.56f, 115.79f, 66.34f, 111.99f, 1.72f }, { 94.46f, 96.22f, 91.53f, 90.47f, 1.72f }, { 123.75f, 89.19f, 123.75f, 82.74f, 1.72f }, { 153.04f, 96.22f, 155.97f, 90.47f, 1.72f }, { 175.95f, 115.79f, 181.17f, 111.99f, 1.72f }, { 187.48f, 143.62f, 193.85f, 142.61f, 1.72f }, { 185.11f, 173.64f, 191.25f, 175.64f, 1.72f }, { 169.37f, 199.33f, 173.94f, 203.89f, 1.72f }, { 263.13f, 199.33f, 258.57f, 203.89f, 1.72f }, { 247.39f, 173.64f, 241.25f, 175.64f, 1.72f }, { 245.03f, 143.62f, 238.66f, 142.61f, 1.72f }, { 256.55f, 115.79f, 251.34f, 111.99f, 1.72f }, { 279.46f, 96.22f, 276.53f, 90.47f, 1.72f }, { 308.75f, 89.19f, 308.75f, 82.74f, 1.72f }, { 338.04f, 96.22f, 340.97f, 90.47f, 1.72f }, { 360.95f, 115.79f, 366.16f, 111.99f, 1.72f }, { 372.47f, 143.62f, 378.84f, 142.61f, 1.72f }, { 370.11f, 173.64f, 376.25f, 175.64f, 1.72f }, { 354.37f, 199.33f, 358.93f, 203.89f, 1.72f }, { 448.13f, 199.33f, 443.56f, 203.89f, 1.72f }, { 432.39f, 173.64f, 426.25f, 175.64f, 1.72f }, { 430.02f, 143.62f, 423.65f, 142.61f, 1.72f }, { 441.55f, 115.79f, 436.33f, 111.99f, 1.72f }, { 464.46f, 96.22f, 461.53f, 90.47f, 1.72f }, { 493.75f, 89.19f, 493.75f, 82.74f, 1.72f }, { 523.04f, 96.22f, 525.97f, 90.47f, 1.72f }, { 545.94f, 115.79f, 551.16f, 111.99f, 1.72f }, { 557.47f, 143.62f, 563.84f, 142.61f, 1.72f }, { 555.11f, 173.64f, 561.24f, 175.64f, 1.72f }, { 539.37f, 199.33f, 543.93f, 203.89f, 1.72f }, { 259.20f, 433.82f, 251.54f, 441.48f, 2.02f }, { 239.11f, 392.12f, 228.35f, 393.33f, 2.02f }, { 249.41f, 346.99f, 240.24f, 341.22f, 2.02f }, { 285.60f, 318.12f, 282.03f, 307.90f, 2.02f }, { 331.90f, 318.12f, 335.47f, 307.90f, 2.02f }, { 368.09f, 346.99f, 377.26f, 341.22f, 2.02f }, { 378.39f, 392.12f, 389.15f, 393.33f, 2.02f }, { 358.30f, 433.82f, 365.96f, 441.48f, 2.02f } };
    const juce::Rectangle<float> rules[] = { { 149.57f, 622.11f, 318.37f, 1.62f } };
    const juce::Point<float> logoPos { 308.75f, 867.64f }; const float logoW = 198.20f;
}
