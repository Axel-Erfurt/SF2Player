# SF2Player
Play Midi Keyboard using Soundfonts and fluidsynth

I wrote it to simply play my midi keyboard on Linux with fluidsynth using pulseaudio.

## Requirements

* python3
* PyQt5
* [fluidsynth](https://github.com/FluidSynth/fluidsynth)
* Soundfont Files (sf2)

## Usage

Start it with

    python3 /path/to/SF2Player.py

or for Gtk Version

    cd /path/to/SF2Player_Gtk.py
    python3 ./SF2Player_Gtk.py
    
After the first start, select a folder with soundfonts with the *Open* button.
Then choose a soundfont in the ComboBox.
Then simply press the start button.

The last used sound font, the window size and position is saved on exit.

![Screenshot](https://github.com/Axel-Erfurt/SF2Player/blob/main/screenshot.png?raw=true)

### SF2PlayerS.py

can use jack

![Screenshot](https://github.com/Axel-Erfurt/SF2Player/blob/main/screenshot2.png?raw=true)
