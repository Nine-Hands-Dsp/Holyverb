#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"

using namespace juce;

namespace
{
    // repere 617,5 x 900 (fond 1235 x 1800 / 2), positions generees par tools/make_art.py dans Layout.h
    // Barre de presets et ligne d'etat AU MEME ENDROIT : une seule pastille 400 x 38 (reference Strong Pickle).
    const Rectangle<float> barRect = layout::presetRect;
    const float barFont = layout::presetFont;

    const float rotStart = MathConstants<float>::pi * 1.25f;    // -135 degres (7 h 30)
    const float rotEnd   = MathConstants<float>::pi * 2.75f;    // +135 degres (4 h 30)

    const Colour inkWhite (0xfff2efe8);     // serigraphie blanc casse
    const Colour ledBlue (0xff3d8bff);
    const Colour screenInk (0xffe8e8ee);
    const Colour panel (0xff08080a);
    const Colour menuAccent (0xffc9a35a);   // or de la cathedrale

    // index = learnDef du processeur : 0 decay, 1 tone, 2 level, 3 mode, 4 predelay, 5 trails, 6 on, 7 expression
    const char* const valueIds[] = { "decay", "tone", "level", "mode", "predelay", "trails", "on", "expression" };
    constexpr int numValueIds = 8;

    float rawOf (HolyverbAudioProcessor& p, const char* id) { return p.apvts.getRawParameterValue (id)->load(); }
    void setParamValue (HolyverbAudioProcessor& p, const char* id, float plain)
    {
        if (auto* prm = p.apvts.getParameter (id))
        {
            prm->beginChangeGesture();
            prm->setValueNotifyingHost (prm->convertTo0to1 (plain));
            prm->endChangeGesture();
        }
    }
}

//==============================================================================
// POTARDS : repere blanc arrondi (de 0,40 a 0,86 du rayon), lumiere fixe en haut a gauche
//==============================================================================
bool HolyKnob::hitTest (int x, int y)
{
    const auto c = getLocalBounds().toFloat().getCentre();
    return c.getDistanceFrom ({ (float) x, (float) y }) <= getWidth() * 0.5f;
}

void HolyKnobLookAndFeel::drawRotarySlider (Graphics& g, int x, int y, int w, int h,
                                            float pos, float startAngle, float endAngle, Slider&)
{
    const auto c = Rectangle<float> ((float) x, (float) y, (float) w, (float) h).getCentre();
    const float R = (float) jmin (w, h) * 0.5f;
    const float a = startAngle + pos * (endAngle - startAngle);
    const Point<float> dir (std::sin (a), -std::cos (a));
    const Point<float> p0 = c + dir * (0.40f * R), p1 = c + dir * (0.86f * R);
    const float lw = jmax (1.4f, 0.062f * R);
    Path line; line.startNewSubPath (p0); line.lineTo (p1);
    g.setColour (Colours::black.withAlpha (0.45f));
    g.strokePath (line, PathStrokeType (lw * 1.15f, PathStrokeType::curved, PathStrokeType::rounded),
                  AffineTransform::translation (R * 0.010f, R * 0.014f));
    const float lightFacing = 0.5f + 0.5f * std::cos (a + MathConstants<float>::pi * 0.25f);
    g.setColour (Colour (0xfff4f4f2).withMultipliedBrightness (0.92f + 0.08f * lightFacing));
    g.strokePath (line, PathStrokeType (lw, PathStrokeType::curved, PathStrokeType::rounded));
}

//==============================================================================
// INVERSEUR (2 positions : haut = 1, bas = 0)
//==============================================================================
LeverSwitch::LeverSwitch (RangedAudioParameter& p)
    : attachment (p, [this] (float v)
                  {
                      const int nf = v > 0.5f ? 2 : 0;
                      if (nf != frame)
                      {
                          frame = targetFrame = nf;
                          shownFrame = 1;                                    // position du milieu ~55 ms
                          transitionUntil = Time::getMillisecondCounterHiRes() + 55.0;
                          repaint();
                      }
                  })
{
    attachment.sendInitialUpdate();
    shownFrame = targetFrame = frame;
    setMouseCursor (MouseCursor::PointingHandCursor);
}

void LeverSwitch::tick (double now)
{
    if (shownFrame != targetFrame && now >= transitionUntil) { shownFrame = targetFrame; repaint(); }
}

void LeverSwitch::paint (Graphics& g)
{
    if (! strip.isValid()) return;
    const int fs = strip.getWidth();
    const int row = 2 - shownFrame;                         // bande : haut / milieu / bas
    g.setImageResamplingQuality (Graphics::highResamplingQuality);
    g.drawImage (strip, 0, 0, getWidth(), getHeight(), 0, row * fs, fs, fs);
}

bool LeverSwitch::hitTest (int x, int y)
{
    const auto c = getLocalBounds().toFloat().getCentre();
    const float r = (float) getWidth() * (layout::togR / layout::togS);
    return std::abs ((float) x - c.x) <= r * 1.15f && std::abs ((float) y - c.y) <= r * 1.6f;
}

void LeverSwitch::moveTo (int nf)
{
    nf = nf >= 1 ? 2 : 0;
    if (nf == frame) return;
    attachment.setValueAsCompleteGesture (nf == 2 ? 1.0f : 0.0f);
    if (onUserChange) onUserChange();
}

void LeverSwitch::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { if (onRightClick) onRightClick(); return; }
    moveTo (frame == 0 ? 2 : 0);
}

void LeverSwitch::mouseWheelMove (const MouseEvent&, const MouseWheelDetails& w)
{
    if (std::abs (w.deltaY) <= 0.0f) return;
    moveTo (w.deltaY > 0 ? 2 : 0);
}

//==============================================================================
// FOOTSWITCH (fonctionnement d'Echoflex)
//==============================================================================
FootSwitchArea::FootSwitchArea (RangedAudioParameter& p)
    : attachment (p, [this] (float v) { value = v > 0.5f; repaint(); })
{
    attachment.sendInitialUpdate();
    setMouseCursor (MouseCursor::PointingHandCursor);
}

bool FootSwitchArea::hitTest (int x, int y)
{
    const auto c = getLocalBounds().toFloat().getCentre();
    return c.getDistanceFrom ({ (float) x, (float) y }) <= (float) getWidth() * (layout::footR * 1.35f / layout::fsS);
}

void FootSwitchArea::paint (Graphics& g)
{
    const auto b = getLocalBounds().toFloat();
    if (ledLevel > 0.003f && reflection.isValid())
    {
        g.setOpacity (ledLevel);
        g.drawImage (reflection, b);
        g.setOpacity (1.0f);
    }
    if (pressed)
    {
        const float r = b.getWidth() * (layout::footR / layout::fsS) * 0.98f;
        const auto c = b.getCentre();
        g.setColour (Colours::black.withAlpha (0.25f));
        g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
    }
}

void FootSwitchArea::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { if (onRightClick) onRightClick(); return; }
    pressed = true;
    repaint();
    attachment.setValueAsCompleteGesture (value ? 0.0f : 1.0f);
    if (onUserChange) onUserChange();
}

void FootSwitchArea::mouseUp (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) return;
    pressed = false;
    repaint();
}

//==============================================================================
// EDITEUR
//==============================================================================
HolyverbAudioProcessorEditor::HolyverbAudioProcessorEditor (HolyverbAudioProcessor& p)
    : AudioProcessorEditor (&p), proc (p),
      preSwitch   (*p.apvts.getParameter (ParamID::preDelay)),
      tailsSwitch (*p.apvts.getParameter (ParamID::trails)),
      footswitch  (*p.apvts.getParameter (ParamID::on))
{
    background = ImageCache::getFromMemory (BinaryData::background_png, BinaryData::background_pngSize);
    glow       = ImageCache::getFromMemory (BinaryData::glow_blue_png, BinaryData::glow_blue_pngSize);
    ledOn      = ImageCache::getFromMemory (BinaryData::led_on_png, BinaryData::led_on_pngSize);
    footswitch.reflection = ImageCache::getFromMemory (BinaryData::fs_refl_png, BinaryData::fs_refl_pngSize);
    const auto strip = ImageCache::getFromMemory (BinaryData::toggle_strip_png, BinaryData::toggle_strip_pngSize);
    labelFace   = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    boldFace    = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize);
    lightFace   = Typeface::createSystemTypefaceFor (BinaryData::PoppinsLight_ttf, BinaryData::PoppinsLight_ttfSize);
    regularFace = Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize);
    menuLnf.f = { regularFace, labelFace, boldFace };
    if (auto xml = XmlDocument::parse (String::fromUTF8 (BinaryData::NineHandsLogo_svg, BinaryData::NineHandsLogo_svgSize)))
        logo = Drawable::createFromSVG (*xml);
    buildPrint();

    rightClickFwd.callback = [this] (Component* c)
    {
        int idx = -1;
        for (int i = 0; i < 4; ++i)
            if (c == &knobs[i]) idx = i;
        showContextMenu (idx);
    };

    const char* ids[4] = { "decay", "tone", "level", "mode" };
    for (int i = 0; i < 4; ++i)
    {
        auto& s = knobs[i];
        s.setSliderStyle (Slider::RotaryHorizontalVerticalDrag);
        s.setTextBoxStyle (Slider::NoTextBox, false, 0, 0);
        s.setRotaryParameters (rotStart, rotEnd, true);
        s.setMouseDragSensitivity (i == 3 ? 160 : 220);
        if (i < 3) s.setDoubleClickReturnValue (true, 0.5);
        s.setLookAndFeel (&lnf);
        s.setMouseCursor (MouseCursor::PointingHandCursor);
        s.addMouseListener (&rightClickFwd, false);
        s.onDragStart = [this] { proc.currentPreset = -1; };
        addAndMakeVisible (s);
        knobAtt[i] = std::make_unique<AudioProcessorValueTreeState::SliderAttachment> (proc.apvts, ids[i], s);
    }

    preSwitch.onRightClick   = [this] { showContextMenu (4); };
    tailsSwitch.onRightClick = [this] { showContextMenu (5); };
    for (auto* l : { &preSwitch, &tailsSwitch })
    {
        l->strip = strip;
        l->onUserChange = [this] { proc.currentPreset = -1; };
        addAndMakeVisible (*l);
    }
    footswitch.onRightClick = [this] { showContextMenu (6); };
    addAndMakeVisible (footswitch);

    for (int i = 0; i < numValueIds; ++i) lastValues[i] = rawOf (proc, valueIds[i]);
    lastPresetCounter = proc.presetCounter.load();
    ledLevel = rawOf (proc, "on") > 0.5f ? 1.0f : 0.0f;
    footswitch.ledLevel = ledLevel;

    // Taille par defaut = taille minimale (impossible de reduire en dessous), proportions bloquees
    const int defaultW = roundToInt ((float) defaultH * baseW / baseH);
    setResizable (true, true);
    setResizeLimits (defaultW, defaultH, roundToInt ((float) maxH * baseW / baseH), maxH);
    if (auto* cons = getConstrainer())
        cons->setFixedAspectRatio ((double) baseW / (double) baseH);
    setOpaque (true);
    setSize (defaultW, defaultH);
    setScaledHeight (sizeHeight (WigaWindowSize::defaultIndex (JucePlugin_Name, numSizes)));
    rebuildCaches();
    startTimerHz (30);
}

HolyverbAudioProcessorEditor::~HolyverbAudioProcessorEditor()
{
    PopupMenu::dismissAllActiveMenus();
    stopTimer();
    for (auto& s : knobs) { s.removeMouseListener (&rightClickFwd); s.setLookAndFeel (nullptr); }
}

//==============================================================================
int HolyverbAudioProcessorEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { (int) defaultH, roundToInt (refH * 0.75f), (int) refH };
    return h[jlimit (0, numSizes - 1, idx)];
}

void HolyverbAudioProcessorEditor::setScaledHeight (int h)
{
    h = jlimit ((int) defaultH, (int) maxH, h);
    setSize (roundToInt ((float) h * baseW / baseH), h);
}

Rectangle<int> HolyverbAudioProcessorEditor::scaled (Rectangle<float> r) const
{
    const float s = (float) getHeight() / baseH;
    return r.transformedBy (AffineTransform::scale (s)).getSmallestIntegerContainer();
}

float HolyverbAudioProcessorEditor::physicalScale() const
{
    if (forcedScale > 0.0f) return forcedScale;
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

void HolyverbAudioProcessorEditor::showStatus() { statusUntil = Time::getMillisecondCounterHiRes() + 2500.0; }

//==============================================================================
// Caches d'affichage (reconstruits par le timer seulement)
//==============================================================================
void HolyverbAudioProcessorEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = cacheScale > 0.0f ? cacheScale : physicalScale();
    const int w = getWidth(), h = getHeight();
    if (w <= 0 || h <= 0) return;
    if (w == cacheW && h == cacheH && std::abs (sc - cacheScale) < 0.01f && bgScaled.isValid()) return;
    cacheW = w; cacheH = h; cacheScale = sc;
    const int pw = roundToInt ((float) w * sc), ph = roundToInt ((float) h * sc);
    bgScaled = (pw >= background.getWidth()) ? background : background.rescaled (pw, ph, Graphics::highResamplingQuality);
    const float s = (float) h / baseH;
    const int gpx = roundToInt (layout::glowRect.getWidth() * s * sc);
    glowS = (gpx >= glow.getWidth()) ? glow : glow.rescaled (gpx, gpx, Graphics::highResamplingQuality);
    repaint();
}

void HolyverbAudioProcessorEditor::resized()
{
    // anti-gel : jamais de setSize ici ; les limites du constrainer suffisent
    for (int i = 0; i < 3; ++i)
    {
        const auto c = layout::knobPos[i]; const float r = layout::knobR;
        knobs[i].setBounds (scaled ({ c.x - r, c.y - r, r * 2.0f, r * 2.0f }));
    }
    {
        const auto c = layout::modePos; const float r = layout::modeR;
        knobs[3].setBounds (scaled ({ c.x - r, c.y - r, r * 2.0f, r * 2.0f }));
    }
    auto lever = [this] (LeverSwitch& l, Point<float> c)
    {
        const float hs = layout::togS * 0.5f;
        const float s = (float) getHeight() / baseH;
        const int side = roundToInt (layout::togS * s);
        l.setBounds (roundToInt ((c.x - hs) * s), roundToInt ((c.y - hs) * s), side, side);
    };
    lever (preSwitch, layout::preDelayPos);
    lever (tailsSwitch, layout::tailsPos);
    const float fr = layout::fsS * 0.5f;
    footswitch.setBounds (scaled ({ layout::fsPos.x - fr, layout::fsPos.y - fr, fr * 2.0f, fr * 2.0f }));
    resizeSettle = 4;
}

//==============================================================================
// Anti-gel v2 (NINE HANDS | DSP)
//==============================================================================
void HolyverbAudioProcessorEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw) peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void HolyverbAudioProcessorEditor::parentHierarchyChanged() { useSoftwareRenderer(); }
void HolyverbAudioProcessorEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

void HolyverbAudioProcessorEditor::askRepaint (Rectangle<int> r)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (r);
}

//==============================================================================
String HolyverbAudioProcessorEditor::buildStatusLine() const
{
    const int i = lastChanged;
    if (i < 0) return {};
    const float v = rawOf (proc, valueIds[i]);
    switch (i)
    {
        case 0: return "Decay  " + String (roundToInt (v * 100.0f)) + " %";
        case 1: return "Tone  " + String (roundToInt (v * 100.0f)) + " %";
        case 2: return "Level  " + String (roundToInt (v * 100.0f)) + " %";
        case 3: { const String n (ModeOrder::name (roundToInt (v))); return "Mode  " + n.substring (0, 1) + n.substring (1).toLowerCase(); }
        case 4: return v > 0.5f ? "Pre-delay  long" : "Pre-delay  short";
        case 5: return v > 0.5f ? "Tails  on (reverb rings out)" : "Tails  cut";
        case 6: return v > 0.5f ? "Effect on" : "Bypass";
        case 7: return "Expression  " + String (roundToInt (v * 100.0f)) + " %";
        default: return {};
    }
}

String HolyverbAudioProcessorEditor::buildPresetLine() const
{
    const int cp = proc.currentPreset.load();
    String s;
    if (cp >= 0 && cp < HolyverbAudioProcessor::getNumFactoryPresets())
        s << "P" << (cp + 1) << "  " << HolyverbAudioProcessor::getFactoryPreset (cp).name;
    else if (cp > 100) s << "User " << (cp - 100);
    else               s << "Edited";
    if (rawOf (proc, "on") < 0.5f) s << "  (bypass)";
    return s;
}

//==============================================================================
void HolyverbAudioProcessorEditor::timerCallback()
{
    const double now = Time::getMillisecondCounterHiRes();
    if (getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = now; useSoftwareRenderer(); }

    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = now;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }

    if (repaintAskedMs > 0.0 && isShowing() && now - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0; lastPeer = nullptr;
        useSoftwareRenderer(); repaint();
    }

    preSwitch.tick (now);
    tailsSwitch.tick (now);

    int changed = -1, numChanged = 0;
    for (int i = 0; i < numValueIds; ++i)
    {
        const float v = rawOf (proc, valueIds[i]);
        if (std::abs (v - lastValues[i]) > 1.0e-4f) { lastValues[i] = v; changed = i; ++numChanged; }
    }
    const int pcount = proc.presetCounter.load();
    if (pcount != lastPresetCounter) { lastPresetCounter = pcount; numChanged = 0; }
    if (numChanged == 1) { lastChanged = changed; showStatus(); learnLineUntil = 0.0; }
    for (int i = 0; i < 4; ++i)
        if (knobs[i].isMouseButtonDown()) { lastChanged = i; showStatus(); learnLineUntil = 0.0; }

    const int lt = proc.learnTarget.load();
    const int learned = proc.lastLearned.exchange (-1);
    if (learned >= 0)
    {
        learnLine = String (HolyverbAudioProcessor::learnDef (learned).name) + " = CC " + String (proc.ccMap[learned].load());
        learnLineUntil = now + 2000.0;
        statusUntil = jmax (statusUntil, learnLineUntil);
    }
    else if (lt >= 0)
    {
        learnLine = "MIDI LEARN  " + String (HolyverbAudioProcessor::learnDef (lt).name);
        learnLineUntil = now + 200.0;
        statusUntil = jmax (statusUntil, now + 200.0);
    }

    const float target = now < statusUntil ? 1.0f : 0.0f;
    statusAlpha += (target - statusAlpha) * (target > statusAlpha ? 0.45f : 0.30f);   // ~120 ms a l'apparition, ~300 ms au retour
    if (statusAlpha < 0.005f) statusAlpha = 0.0f;
    if (statusAlpha > 0.995f) statusAlpha = 1.0f;

    // LED bleue : allumage / extinction en fondu, lueur qui respire avec la reverb
    const bool on = footswitch.isOn();
    ledLevel += ((on ? 1.0f : 0.0f) - ledLevel) * (on ? 0.45f : 0.28f);
    if (ledLevel < 0.003f) ledLevel = 0.0f;
    if (ledLevel > 0.997f) ledLevel = 1.0f;
    const float wetNow = jlimit (0.0f, 1.0f, std::sqrt (proc.ledLevel.load()) * 2.4f);
    reverbGlow += (wetNow - reverbGlow) * (wetNow > reverbGlow ? 0.45f : 0.10f);
    const float ledNow = ledLevel * (0.82f + 0.18f * reverbGlow);
    if (std::abs (ledNow - drawnLed) > 0.004f)
    {
        drawnLed = ledNow;
        footswitch.ledLevel = ledLevel;
        askRepaint (scaled (layout::glowRect));
        footswitch.repaint();
    }

    const auto l1 = (learnLineUntil > 0.0 && now < learnLineUntil + 800.0 ? learnLine : buildStatusLine()), pl = buildPresetLine();
    const bool textChanged = l1 != lastLine1;
    lastLine1 = l1;
    if (std::abs (statusAlpha - drawnStatus) > 0.003f || (statusAlpha > 0.0f && textChanged))
    {
        drawnStatus = statusAlpha;
        askRepaint (scaled (barRect.expanded (3.0f)));
    }
    if (pl != lastPreset || hoverZone != drawnHover)
    {
        lastPreset = pl; drawnHover = hoverZone;
        askRepaint (scaled (barRect.expanded (3.0f)));
    }
}

//==============================================================================
// Serigraphie vectorielle : construite une fois en chemins (unites du plugin), remplie a l'echelle de la fenetre
//==============================================================================
static Path textPath (const layout::Txt& t, const Typeface::Ptr& face)
{
    const Font font (FontOptions (face).withPointHeight (t.em));
    const String s (t.s);
    float total = 0.0f;
    for (int i = 0; i < s.length(); ++i)
        total += GlyphArrangement::getStringWidth (font, String::charToString (s[i])) + (i > 0 ? t.track : 0.0f);
    const float base = (font.getAscent() - font.getDescent()) * 0.5f;
    GlyphArrangement ga;
    float x = -total * 0.5f;
    for (int i = 0; i < s.length(); ++i)
    {
        const String ch = String::charToString (s[i]);
        ga.addLineOfText (font, ch, x, base);
        x += GlyphArrangement::getStringWidth (font, ch) + t.track;
    }
    Path p; ga.createPath (p);
    p.applyTransform (AffineTransform::rotation (-t.rot * MathConstants<float>::pi / 180.0f).translated (t.x, t.y));
    return p;
}

void HolyverbAudioProcessorEditor::buildPrint()
{
    printPath.clear();
    auto faceOf = [this] (int f) { return f == 1 ? boldFace : (f == 2 ? lightFace : labelFace); };
    for (const auto& t : layout::texts) printPath.addPath (textPath (t, faceOf (t.font)));
    for (const auto& k : layout::ticks)
    {
        Path seg; seg.startNewSubPath (k.x0, k.y0); seg.lineTo (k.x1, k.y1);
        Path stroked;
        PathStrokeType (k.w, PathStrokeType::curved, PathStrokeType::rounded).createStrokedPath (stroked, seg);
        printPath.addPath (stroked);
    }
    for (const auto& r : layout::rules) printPath.addRectangle (r);
}

void HolyverbAudioProcessorEditor::drawPrint (Graphics& g)
{
    g.setColour (inkWhite);
    g.fillPath (printPath);
    if (logo != nullptr)
    {
        const auto vb = logo->getDrawableBounds();
        const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        logo->drawWithin (g, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }, RectanglePlacement::centred, 0.92f);
    }
}

void HolyverbAudioProcessorEditor::drawGlow (Graphics& g)
{
    // facade eclairee par la LED (calque alpha precalcule), sous la serigraphie : jamais de texte masque
    const float lv = ledLevel * (0.82f + 0.18f * reverbGlow);
    if (lv <= 0.003f) return;
    const Image& img = glowS.isValid() ? glowS : glow;
    if (! img.isValid()) return;
    g.setOpacity (jmin (1.0f, lv)); g.drawImage (img, layout::glowRect); g.setOpacity (1.0f);
}

void HolyverbAudioProcessorEditor::drawLed (Graphics& g)
{
    const float level = ledLevel;
    if (level <= 0.003f) return;
    const auto c = layout::ledPos;
    const float hs = layout::ledS * 0.5f;
    if (ledOn.isValid()) { g.setOpacity (level); g.drawImage (ledOn, { c.x - hs, c.y - hs, hs * 2.0f, hs * 2.0f }); }
    g.setOpacity (1.0f);
    const float hr = 20.0f, lv = level * (0.82f + 0.18f * reverbGlow);
    ColourGradient halo (ledBlue.withAlpha (0.26f * lv), c.x, c.y, ledBlue.withAlpha (0.0f), c.x + hr, c.y, true);
    halo.addColour (0.4, ledBlue.withAlpha (0.07f * lv));
    g.setGradientFill (halo);
    g.fillEllipse (c.x - hr, c.y - hr, hr * 2.0f, hr * 2.0f);
}

void HolyverbAudioProcessorEditor::drawStatus (Graphics& g)
{
    // pastille unique : fond + contour (la ligne d'etat et la barre de presets s'y relaient en fondu croise)
    const auto r = barRect;
    g.setColour (panel.withAlpha (0.84f));
    g.fillRoundedRectangle (r, r.getHeight() * 0.5f);
    g.setColour (Colour (0xffc9a35a).withAlpha (hoverZone != 0 && statusAlpha <= 0.0f ? 0.55f : 0.30f));
    g.drawRoundedRectangle (r.reduced (0.6f), r.getHeight() * 0.5f, 1.2f);
    const float a = statusAlpha;
    if (a <= 0.0f) return;
    g.setFont (Font (FontOptions (labelFace).withHeight (barFont)));
    g.setColour (screenInk.withAlpha (a));
    g.drawFittedText (lastLine1, r.reduced (r.getHeight() * 0.5f, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
}

void HolyverbAudioProcessorEditor::drawPresetBar (Graphics& g)
{
    const float a = 1.0f - statusAlpha;
    if (a <= 0.0f) return;
    const auto r = barRect;
    const float aw = 34.0f;
    auto arrow = [&] (Rectangle<float> ar, bool left, bool hot)
    {
        Path p; const auto c = ar.getCentre(); const float sz = 5.5f;
        if (left) p.addTriangle (c.x + sz * 0.6f, c.y - sz, c.x + sz * 0.6f, c.y + sz, c.x - sz * 0.8f, c.y);
        else      p.addTriangle (c.x - sz * 0.6f, c.y - sz, c.x - sz * 0.6f, c.y + sz, c.x + sz * 0.8f, c.y);
        g.setColour (screenInk.withAlpha ((hot ? 1.0f : 0.6f) * a));
        g.fillPath (p);
    };
    arrow (r.withWidth (aw), true, hoverZone == 1);
    arrow (r.withTrimmedLeft (r.getWidth() - aw), false, hoverZone == 3);
    g.setFont (Font (FontOptions (labelFace).withHeight (barFont)));
    g.setColour (screenInk.withAlpha ((hoverZone == 2 ? 1.0f : 0.92f) * a));
    g.drawFittedText (lastPreset, r.reduced (aw, 0.0f).toNearestInt(), Justification::centred, 1, 0.7f);
}

void HolyverbAudioProcessorEditor::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (0xff111112));          // autour des jacks : le fond de l'image est transparent
    const Image& bg = bgScaled.isValid() ? bgScaled : background;
    g.setImageResamplingQuality (&bg == &background ? Graphics::highResamplingQuality : Graphics::lowResamplingQuality);
    if (bg.isValid()) g.drawImage (bg, getLocalBounds().toFloat());

    const float s = (float) getHeight() / baseH;
    g.addTransform (AffineTransform::scale (s));
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
    drawGlow (g);
    drawStatus (g);
    drawPresetBar (g);
    drawPrint (g);
    drawLed (g);
}

//==============================================================================
// Souris : barre de presets (fleches = precedent / suivant, nom = menu deroulant), clic droit = menu
//==============================================================================
static int presetZoneAt (Point<float> p)
{
    if (! barRect.contains (p)) return 0;
    if (p.x < barRect.getX() + 34.0f) return 1;
    if (p.x > barRect.getRight() - 34.0f) return 3;
    return 2;
}

void HolyverbAudioProcessorEditor::mouseMove (const MouseEvent& e)
{
    const float s = (float) getHeight() / baseH;
    hoverZone = presetZoneAt (e.position / s);
    setMouseCursor (hoverZone != 0 ? MouseCursor::PointingHandCursor : MouseCursor::NormalCursor);
}

void HolyverbAudioProcessorEditor::mouseExit (const MouseEvent&) { hoverZone = 0; }

void HolyverbAudioProcessorEditor::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { showContextMenu(); return; }
    const float s = (float) getHeight() / baseH;
    if (statusAlpha > 0.0f && barRect.contains (e.position / s))
    {   // la ligne d'etat ne bloque pas : un clic fait revenir la barre de presets
        statusUntil = 0.0; learnLineUntil = 0.0;
        return;
    }
    switch (presetZoneAt (e.position / s))
    {
        case 1: stepPreset (-1); break;
        case 2: showPresetMenu(); break;
        case 3: stepPreset (1); break;
        default: break;
    }
}

void HolyverbAudioProcessorEditor::stepPreset (int delta)
{
    const int n = HolyverbAudioProcessor::getNumFactoryPresets();
    int cp = proc.currentPreset.load();
    if (cp < 0 || cp >= n) cp = delta > 0 ? -1 : 0;
    proc.applyFactoryPreset ((cp + delta + n) % n);
}

void HolyverbAudioProcessorEditor::showPresetMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    NineHandsMenu::addHeader (m, menuLnf.f, NineHandsMenu::icoPreset, menuAccent, "Presets", buildPresetLine());
    m.addSectionHeader ("Factory presets");
    for (int i = 0; i < HolyverbAudioProcessor::getNumFactoryPresets(); ++i)
        m.addItem (100 + i, String (i + 1) + ". " + HolyverbAudioProcessor::getFactoryPreset (i).name, true, proc.currentPreset.load() == i);
    m.addSeparator();
    PopupMenu load, save;
    for (int slot = 1; slot <= 9; ++slot)
    {
        const bool exists = proc.hasUserPreset (slot);
        load.addItem (200 + slot, "User " + String (slot) + (exists ? "" : "  (empty)"), exists, proc.currentPreset.load() == 100 + slot);
        save.addItem (300 + slot, "User " + String (slot) + (exists ? "  (overwrite)" : ""));
    }
    m.addSubMenu ("Load user preset", load);
    m.addSubMenu ("Save user preset", save);

    m.showMenuAsync (PopupMenu::Options().withTargetScreenArea (localAreaToGlobal (scaled (barRect))),
        [safe = Component::SafePointer<HolyverbAudioProcessorEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& pr = safe->proc;
            if      (r >= 100 && r < 200) pr.applyFactoryPreset (r - 100);
            else if (r > 200 && r < 300)  pr.loadUserPreset (r - 200);
            else if (r > 300 && r < 400)  pr.saveUserPreset (r - 300);
            safe->showStatus();
        });
}

void HolyverbAudioProcessorEditor::handleMidiMenu (int r)
{
    if (r >= 1000 && r < 1000 + HolyverbAudioProcessor::numLearn)      proc.learnTarget.store (r - 1000);
    else if (r >= 1100 && r < 1100 + HolyverbAudioProcessor::numLearn) proc.ccMap[r - 1100].store (-1);
    else if (r == 1200) proc.learnTarget.store (-1);
    else if (r == 1201) { proc.learnTarget.store (-1); proc.resetMidiMap(); }
}

void HolyverbAudioProcessorEditor::showContextMenu (int learnIdx)
{
    using namespace NineHandsMenu;
    PopupMenu menu;
    menu.setLookAndFeel (&menuLnf);
    auto ccText = [this] (int i)
    {
        const int cc = proc.ccMap[i].load();
        return cc >= 0 ? "CC " + String (cc) : String ("not assigned");
    };
    const int lt = proc.learnTarget.load();
    if (learnIdx >= 0)
    {
        const String name = HolyverbAudioProcessor::learnDef (learnIdx).name;
        const int ico = learnIdx < 4 ? icoKnob : (learnIdx == 6 ? icoPedal : icoSwitch);
        addHeader (menu, menuLnf.f, ico, menuAccent, name, "MIDI: " + ccText (learnIdx));
        menu.addItem (1000 + learnIdx, "MIDI Learn: " + name, true, lt == learnIdx);
        menu.addItem (1100 + learnIdx, "Clear MIDI: " + name, proc.ccMap[learnIdx].load() >= 0);
        if (lt >= 0) menu.addItem (1200, "Cancel MIDI learn");
        menu.addSeparator();
    }
    else
        addHeader (menu, menuLnf.f, icoPedal, menuAccent, "Holyverb", "Reverb  v" + String (JucePlugin_VersionString));

    PopupMenu sizes;
    {
        const char* names[numSizes] = { "60 %", "75 %", "100 %" };
        const int def = WigaWindowSize::defaultIndex (JucePlugin_Name, numSizes);
        PopupMenu defSizes;
        for (int i = 0; i < numSizes; ++i)
        {
            sizes.addItem (1 + i, String (names[i]) + (i == def ? "  (default)" : ""), true, std::abs (getHeight() - sizeHeight (i)) <= 2);
            defSizes.addItem (20 + i, names[i], true, i == def);
        }
        sizes.addSeparator();
        sizes.addSubMenu ("Default size (new windows)", defSizes);
    }
    menu.addSubMenu ("Plugin size", sizes);
    menu.addSeparator();

    PopupMenu factory;
    for (int i = 0; i < HolyverbAudioProcessor::getNumFactoryPresets(); ++i)
        factory.addItem (100 + i, String (i + 1) + ". " + HolyverbAudioProcessor::getFactoryPreset (i).name, true, proc.currentPreset.load() == i);
    menu.addSubMenu ("Factory presets", factory);
    PopupMenu load, save;
    for (int slot = 1; slot <= 9; ++slot)
    {
        const bool exists = proc.hasUserPreset (slot);
        load.addItem (200 + slot, "User " + String (slot) + (exists ? "" : "  (empty)"), exists, proc.currentPreset.load() == 100 + slot);
        save.addItem (300 + slot, "User " + String (slot) + (exists ? "  (overwrite)" : ""));
    }
    menu.addSubMenu ("Load user preset", load);
    menu.addSubMenu ("Save user preset", save);
    menu.addSeparator();

    PopupMenu modes;
    const int cur = roundToInt (rawOf (proc, "mode"));
    for (int i = 0; i < 8; ++i)
    {
        const String n (ModeOrder::name (i));
        modes.addItem (400 + i, n.substring (0, 1) + n.substring (1).toLowerCase(), true, cur == i);
    }
    menu.addSubMenu ("Mode", modes);
    menu.addItem (52, "Reset expression", rawOf (proc, "expression") > 0.001f);

    PopupMenu settings;
    settings.addItem (41, "MIDI footswitch latching (127 = on / 0 = off)", true, ! proc.midiFsMomentary.load());
    settings.addItem (42, "MIDI footswitch momentary (toggle each press)", true, proc.midiFsMomentary.load());
    menu.addSubMenu ("Settings", settings);

    PopupMenu midi;
    midi.addSectionHeader ("MIDI Learn");
    for (int i = 0; i < HolyverbAudioProcessor::numLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (HolyverbAudioProcessor::learnDef (i).name) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    if (lt >= 0) midi.addItem (1200, "Cancel MIDI learn");
    midi.addItem (1201, "Clear all MIDI assignments");
    menu.addSubMenu ("MIDI", midi);
    menu.addSeparator();
    menu.addItem (999, "Holyverb v" + String (JucePlugin_VersionString) + "  NINE HANDS | DSP", false);

    menu.showMenuAsync (PopupMenu::Options().withMousePosition(),    // menu clic droit : toujours la ou l'on clique
        [safe = Component::SafePointer<HolyverbAudioProcessorEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& ed = *safe;
            auto& pr = ed.proc;
            if      (r >= 1 && r < 1 + numSizes) ed.setScaledHeight (ed.sizeHeight (r - 1));
            else if (r >= 20 && r < 20 + numSizes)
            {
                WigaWindowSize::setDefaultIndex (JucePlugin_Name, r - 20);
                ed.setScaledHeight (ed.sizeHeight (r - 20));
            }
            else if (r == 41) pr.midiFsMomentary.store (false);
            else if (r == 42) pr.midiFsMomentary.store (true);
            else if (r == 52) setParamValue (pr, "expression", 0.0f);
            else if (r >= 100 && r < 200) pr.applyFactoryPreset (r - 100);
            else if (r > 200 && r < 300)  pr.loadUserPreset (r - 200);
            else if (r > 300 && r < 400)  pr.saveUserPreset (r - 300);
            else if (r >= 400 && r < 408) { setParamValue (pr, "mode", (float) (r - 400)); pr.currentPreset = -1; }
            else if (r >= 1000) { ed.handleMidiMenu (r); return; }
            ed.showStatus();
        });
}
