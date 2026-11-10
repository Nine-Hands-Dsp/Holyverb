# Outil hors plugin : compile le processeur + la fenetre de HOLYVERB sous Linux et exporte des captures PNG (apercu, notice)
cmake_minimum_required(VERSION 3.22)
project(HolyverbRender VERSION 1.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
set(W ${CMAKE_CURRENT_SOURCE_DIR}/../..)
juce_add_binary_data(HolyverbAssets SOURCES
  ${W}/background.png ${W}/toggle_strip.png ${W}/glow_blue.png ${W}/led_on.png ${W}/fs_refl.png
  ${W}/Poppins-Medium.ttf ${W}/Poppins-Bold.ttf ${W}/Poppins-Light.ttf ${W}/Poppins-Regular.ttf ${W}/NineHandsLogo.svg)
juce_add_console_app(HolyverbRender PRODUCT_NAME "HolyverbRender")
target_sources(HolyverbRender PRIVATE main.cpp ${W}/Source/PluginProcessor.cpp ${W}/Source/PluginEditor.cpp)
target_include_directories(HolyverbRender PRIVATE ${W} ${W}/Source)
target_compile_definitions(HolyverbRender PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_ALSA=0 JUCE_JACK=0
  JUCE_USE_XRANDR=0 JUCE_USE_XINERAMA=0 JUCE_USE_XCURSOR=0 JUCE_USE_XSHM=0 JucePlugin_Name="Holyverb" JucePlugin_Build_VST3=0
  JucePlugin_VersionString="1.6.0" JUCE_STANDALONE_APPLICATION=1 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(HolyverbRender PRIVATE HolyverbAssets juce::juce_audio_utils juce::juce_dsp juce::juce_recommended_config_flags)
