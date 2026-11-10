#pragma once

#include "PluginProcessor.h"
#include <juce_gui_basics/juce_gui_basics.h>
#include "Layout.h"
#include "NineHandsMenu.h"

//==============================================================================
// Holyverb v1.6 (NINE HANDS | DSP) : pedale simple 1235 x 1800, pieces photo du kit.
// Potards (photo, dans le fond : reflets fixes) : seul le repere blanc peint tourne.
//==============================================================================
class HolyKnobLookAndFeel : public juce::LookAndFeel_V4
{
public:
    void drawRotarySlider (juce::Graphics&, int x, int y, int w, int h,
                           float pos, float startAngle, float endAngle, juce::Slider&) override;
};

class HolyKnob : public juce::Slider
{
public:
    bool hitTest (int x, int y) override;
};

//==============================================================================
// Inverseur a levier 2 positions (photos du kit haut / milieu / bas recalees : rien ne bouge a part le levier).
// Image du milieu ~55 ms pendant la bascule. Les trois images sont dessinees dans le meme rectangle.
//==============================================================================
class LeverSwitch : public juce::Component
{
public:
    explicit LeverSwitch (juce::RangedAudioParameter& p);
    void paint (juce::Graphics&) override;
    bool hitTest (int x, int y) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;
    void tick (double nowMs);
    juce::Image strip;
    std::function<void()> onRightClick, onUserChange;

private:
    void moveTo (int newFrame);
    juce::ParameterAttachment attachment;
    int frame = 0, shownFrame = 0, targetFrame = 0;     // 0 = bas, 1 = milieu, 2 = haut
    double transitionUntil = 0.0;
};

//==============================================================================
// Footswitch (photo du kit, dans le fond) : fonctionnement d'Echoflex ; reflet bleu de la LED en fondu.
//==============================================================================
class FootSwitchArea : public juce::Component
{
public:
    explicit FootSwitchArea (juce::RangedAudioParameter& p);
    void paint (juce::Graphics&) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    bool hitTest (int x, int y) override;
    bool isOn() const { return value; }
    std::function<void()> onRightClick, onUserChange;
    juce::Image reflection;
    float ledLevel = 0.0f;
private:
    bool value = true, pressed = false;
    juce::ParameterAttachment attachment;
};

struct RightClickForwarder : public juce::MouseListener
{
    std::function<void (juce::Component*)> callback;
    void mouseDown (const juce::MouseEvent& e) override { if (e.mods.isPopupMenu() && callback) callback (e.eventComponent); }
};

//==============================================================================
class HolyverbAudioProcessorEditor : public juce::AudioProcessorEditor,
                                     private juce::Timer
{
public:
    explicit HolyverbAudioProcessorEditor (HolyverbAudioProcessor&);
    ~HolyverbAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;

    // Repere du fond (pedale plein cadre, image 1235 x 1800 px / 2). Hauteurs de fenetre des pedales simples :
    // taille par defaut = taille minimale 493 px (« 60 % »), 100 % = 958 px, jusqu'a 150 %.
    static constexpr float baseW = layout::frameW;
    static constexpr float baseH = layout::frameH;
    static constexpr int defaultH = 493;
    static constexpr int refH = 958;
    static constexpr int maxH = refH * 3 / 2;

    void setScaledHeight (int h);
    void forceRenderScale (float sc) { forcedScale = sc; rebuildCaches (sc); }   // captures (outil de rendu)
    static constexpr int numSizes = 3;          // 60 % (defaut) / 75 % / 100 %
    static int sizeHeight (int idx);
    void showStatus();
    void openMainMenu() { showContextMenu(); }  // outil de rendu (capture du menu)

private:
    void timerCallback() override;
    void useSoftwareRenderer();
    void visibilityChanged() override;
    void askRepaint (juce::Rectangle<int> r);
    void showContextMenu (int learnIdx = -1);
    void handleMidiMenu (int r);
    void showPresetMenu();
    void stepPreset (int delta);
    void rebuildCaches (float scale = 0.0f);
    float physicalScale() const;
    juce::Rectangle<int> scaled (juce::Rectangle<float> r) const;
    juce::String buildStatusLine() const;
    juce::String buildPresetLine() const;
    void buildPrint();
    void drawPrint (juce::Graphics&);
    void drawGlow (juce::Graphics&);
    void drawLed (juce::Graphics&);
    void drawStatus (juce::Graphics&);
    void drawPresetBar (juce::Graphics&);

    HolyverbAudioProcessor& proc;
    HolyKnobLookAndFeel lnf;
    NineHandsMenu::MenuLnf menuLnf;
    RightClickForwarder rightClickFwd;

    juce::Image background, bgScaled, glow, glowS, ledOn;
    int cacheW = 0, cacheH = 0;
    float cacheScale = 0.0f, forcedScale = 0.0f;
    int resizeSettle = 0;
    void* lastPeer = nullptr;
    double lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0;
    juce::Typeface::Ptr labelFace, boldFace, lightFace, regularFace;
    juce::Path printPath;
    std::unique_ptr<juce::Drawable> logo;

    HolyKnob knobs[4];                          // decay, tone, level, mode
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> knobAtt[4];
    LeverSwitch preSwitch, tailsSwitch;
    FootSwitchArea footswitch;

    float ledLevel = 1.0f, ledFlicker = 1.0f, reverbGlow = 0.0f, drawnLed = -1.0f;
    juce::Random rng;
    int lastChanged = -1;
    float statusAlpha = 0.0f, drawnStatus = -1.0f;
    double statusUntil = 0.0;
    juce::String lastLine1, lastPreset;
    juce::String learnLine;
    double learnLineUntil = 0.0;
    float lastValues[8];
    int lastPresetCounter = 0;
    int hoverZone = 0, drawnHover = -1;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (HolyverbAudioProcessorEditor)
};
