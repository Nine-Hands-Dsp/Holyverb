// Captures PNG de la fenetre reelle de Holyverb (meme code que le plugin), pour l'apercu et la notice.
#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "BinaryData.h"
using namespace juce;
static void setP (HolyverbAudioProcessor& p, const char* id, float plain)
{
    if (auto* q = p.apvts.getParameter (id)) q->setValueNotifyingHost (q->convertTo0to1 (plain));
}
int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI init;
    const String out = argc > 1 ? argv[1] : ".";
    HolyverbAudioProcessor proc;
    proc.prepareToPlay (48000.0, 256);
    std::unique_ptr<AudioProcessorEditor> ed (proc.createEditor());
    auto* ped = static_cast<HolyverbAudioProcessorEditor*> (ed.get());
    std::printf ("taille par defaut : %d x %d\n", ed->getWidth(), ed->getHeight());
    auto pump = [] (int n) { for (int i = 0; i < n; ++i) MessageManager::getInstance()->runDispatchLoopUntil (40); };
    auto feed = [&]
    {
        AudioBuffer<float> b (2, 256); MidiBuffer m;
        for (int i = 0; i < 40; ++i) { b.clear(); if (i < 4) b.setSample (0, 0, 0.8f), b.setSample (1, 0, 0.8f); proc.processBlock (b, m); }
    };
    auto save = [&] (const String& name, float scale)
    {
        auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, scale);
        File f (out + "/" + name + ".png"); f.deleteFile();
        FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        std::printf ("%s (%d x %d)\n", f.getFullPathName().toRawUTF8(), img.getWidth(), img.getHeight());
    };
    auto shot = [&] (const String& name, int preset, bool on, bool status, int height)
    {
        ped->setScaledHeight (height); ped->forceRenderScale (2.0f);
        proc.applyFactoryPreset (preset); setP (proc, "on", on ? 1.f : 0.f);
        feed(); pump (30);
        if (status) setP (proc, "decay", 0.64f); else pump (100);
        pump (12);
        save (name, 2.0f);
    };
    shot ("holy_default", 0, true, false, HolyverbAudioProcessorEditor::defaultH);
    shot ("holy_status", 0, true, true, HolyverbAudioProcessorEditor::refH);
    shot ("holy_bypass", 7, false, false, HolyverbAudioProcessorEditor::refH);
    // rendu exact de la pedale seule (1235 x 1800)
    auto exact = [&] (const String& name, int preset, bool on)
    {
        ped->setScaledHeight (900); ped->forceRenderScale (2.0f);
        proc.applyFactoryPreset (preset); setP (proc, "on", on ? 1.f : 0.f);
        feed(); pump (140);
        save (name, 1800.0f / (float) ed->getHeight());
    };
    exact ("holy_exact", 11, true);          // Heaven Shimmer : PRE DELAY long (haut), TAILS (haut)
    exact ("holy_exact_hall", 0, true);      // Concert Hall : PRE DELAY short (bas)
    exact ("holy_exact_bypass", 0, false);
    {   // inverseur : haut / milieu (pendant la bascule) / bas
        ped->setScaledHeight (900); ped->forceRenderScale (2.0f);
        setP (proc, "predelay", 1.f); pump (10); save ("anim_0_haut", 2.0f);
        setP (proc, "predelay", 0.f); save ("anim_1_milieu", 2.0f);
        pump (10); save ("anim_2_bas", 2.0f);
    }
    {   // menus (design Octopus)
        NineHandsMenu::MenuLnf lnf;
        lnf.f = { Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize) };
        struct It { String text; bool sep, sub, ticked, active; };
        auto render = [&] (const String& name, const String& title, const String& subtitle, int ico, const std::vector<It>& items, int hiIndex)
        {
            NineHandsMenu::Header hd (lnf.f, ico, Colour (0xffc9a35a), title, subtitle);
            int w = 0, h = 0; hd.getIdealSize (w, h);
            const int border = lnf.getPopupMenuBorderSize();
            int totalH = border * 2 + h + 11, maxW = w;
            for (auto& it : items) { int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih); totalH += ih; maxW = jmax (maxW, iw + (it.sub ? 20 : 0)); }
            maxW += border * 2;
            Image img (Image::ARGB, maxW * 2, totalH * 2, true);
            Graphics g (img); g.addTransform (AffineTransform::scale (2.0f));
            lnf.drawPopupMenuBackground (g, maxW, totalH);
            int y = border;
            hd.setSize (maxW - border * 2, h);
            { Graphics::ScopedSaveState ss (g); g.setOrigin (border, y); hd.paint (g); }
            y += h;
            lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, 11 }, true, true, false, false, false, {}, {}, nullptr, nullptr); y += 11;
            for (size_t i = 0; i < items.size(); ++i)
            {
                const auto& it = items[i]; int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih);
                lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, ih }, it.sep, it.active, (int) i == hiIndex, it.ticked, it.sub, it.text, {}, nullptr, nullptr);
                y += ih;
            }
            File f (out + "/" + name + ".png"); f.deleteFile();
            FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        };
        render ("holy_menu", "Holyverb", "Reverb  v1.6.0", NineHandsMenu::icoPedal,
                { { "Plugin size", false, true, false, true }, { "", true }, { "Factory presets", false, true, false, true },
                  { "Load user preset", false, true, false, true }, { "Save user preset", false, true, false, true }, { "", true },
                  { "Mode", false, true, false, true }, { "Reset expression", false, false, false, false },
                  { "Settings", false, true, false, true }, { "MIDI", false, true, false, true },
                  { "", true }, { "Holyverb v1.6.0  NINE HANDS | DSP", false, false, false, false } }, 2);
        render ("holy_menu_knob", "Decay", "MIDI: not assigned", NineHandsMenu::icoKnob,
                { { "MIDI Learn: Decay", false, false, false, true }, { "Clear MIDI: Decay", false, false, false, false }, { "", true },
                  { "Plugin size", false, true, false, true }, { "", true }, { "Factory presets", false, true, false, true } }, 0);
    }
    ed.reset();
    return 0;
}
