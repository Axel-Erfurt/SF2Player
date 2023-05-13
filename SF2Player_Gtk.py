#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
import subprocess

from pathlib import Path
import configparser

conf_path = Path('config.conf').resolve()
config = configparser.ConfigParser()

start_icon = str(Path("piano.png").resolve())
stop_icon = str(Path("piano_stop.png").resolve())

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.sf_path = ""
        self.path_list = []
        self.name_list = []
        self.start_img = True
        self.use_jack = False
        self.sf2_file = ""
        self.connect("destroy", self.handle_close)
        self.set_title("SF2Player")
        self.set_default_size(450, 250)
        self.set_resizable(False)

        grid = Gtk.VBox()
        self.add(grid)
        
        self.statusbar = Gtk.Statusbar()
        self.statusbar.set_halign(3)

        img = Gtk.Image.new_from_icon_name("document-open", 2)
        self.sf_folder_btn = Gtk.Button(image = img, margin_top=10, tooltip_text = "choose Soundfont Folder ...")
        self.sf_folder_btn.set_halign(3)
        self.sf_folder_btn.connect("clicked", self.on_open_folder)
        grid.pack_start(self.sf_folder_btn, False, False, 0)
        
        self.sf_combo = Gtk.ComboBoxText(margin_top=10)
        self.sf_combo.set_halign(3)
        self.sf_combo.connect("changed", self.on_sf_combo_changed)
        self.sf_combo.set_tooltip_text("choose Soundfont ...")
        grid.pack_start(self.sf_combo, False, False, 0)
        
        self.check_jack = Gtk.CheckButton(label = "use jack")
        self.check_jack.connect("toggled", self.on_check_jack_changed)
        self.check_jack.set_halign(3)
        grid.pack_start(self.check_jack, False, False, 10)
        
        img = Gtk.Image.new_from_file(start_icon)
        self.btn_start = Gtk.Button(label="Start", image=img, margin_top=20)
        self.btn_start.set_halign(3)
        self.btn_start.connect("clicked", self.on_btn_start_clicked)
        grid.pack_start(self.btn_start, False, False, 10)
        
        self.statusbar.push(0,"Choose Folder with button on top")
        
        grid.pack_end(self.statusbar, False, False, 10)
        
        self.read_config() 

        
        self.show_all()
        
    def on_open_folder(self, *args):
            dialog = Gtk.FileChooserDialog(
                title="Please choose a folder",
                parent=None,
                action=Gtk.FileChooserAction.SELECT_FOLDER,
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
            )
            dialog.set_default_size(600, 400)
    
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.sf_path = dialog.get_filename()
                self.sf_combo.remove_all()
                for root, dirs, files in os.walk(self.sf_path, topdown = False):
                   for name in files:
                      if name.endswith(".sf2"):
                          self.name_list.append(name)
                          self.sf_combo.append_text(name)      
                
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancelled")
    
            dialog.destroy()
        
    def on_sf_combo_changed(self, combo, *args):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            sf2 = model[tree_iter][0]
            self.sf2_file = f"{self.sf_path}/{sf2}"
            print(f"Selected:  {self.sf2_file}")
            self.statusbar.push(0, f"{sf2} selected")
            
    def on_btn_start_clicked(self, btn, *args):
        start_icon_img = Gtk.Image.new_from_file(start_icon)
        stop_icon_img = Gtk.Image.new_from_file(stop_icon)
        if self.start_img:
            btn.set_image(stop_icon_img)
            btn.set_label("Stop")
            self.start_img = False
            self.statusbar.push(0, "Server started ...")
            self.start_server()
        else:
            btn.set_image(start_icon_img)
            btn.set_label("Start")
            self.start_img = True
            self.statusbar.push(0, "Server stopped")
            subprocess.Popen(["killall", "fluidsynth"])
            
    def on_check_jack_changed(self, chk, *args):
        state = chk.get_active()
        self.use_jack = state
        
    def start_server(self):
        if self.use_jack:
            cmd_start = ('fluidsynth --server --no-shell -p "mysynth" --audio-driver=jack --connect-jack-outputs --reverb=20 --chorus=0 --gain=1.8 -o midi.autoconnect=true  &>/tmp/fluidsynth.out').split(" ")
        else:
            cmd_start = ('fluidsynth --server --no-shell -p "mysynth" --audio-driver=pulseaudio --reverb=20 --chorus=0 --gain=1.8 -o midi.autoconnect=true  &>/tmp/fluidsynth.out').split(" ")
        cmd_start[12] = self.sf2_file
        print(cmd_start)
        subprocess.Popen(cmd_start)
        
    def write_config(self, *args):
        if Path.is_file(conf_path):
            print("config_file exists")
        else:
           Path(conf_path).touch()

        config.read(conf_path)
        
        if not config.has_section('SFPath'):
            config.add_section('SFPath')
        config['SFPath']['path'] = self.sf_path

        if not config.has_section('Recent'):
            config.add_section('Recent')
        config['Recent']['lastfile'] = self.sf_combo.get_active_text()
        config['Recent']['last_index'] = str(self.sf_combo.get_active())
        config['Recent']['jack_used'] = str(self.check_jack.get_active())
            
        with open(conf_path, 'w') as configfile:
            config.write(configfile)

    def read_config(self, *args):
        config.read(conf_path)

        if config.has_section('SFPath'):
            self.sf_path = config['SFPath']['path']
            print(self.sf_path)
            
        for root, dirs, files in os.walk(self.sf_path, topdown = False):
           for name in files:
              if name.endswith(".sf2"):
                  self.name_list.append(name)
                  self.sf_combo.append_text(name)   
            
        if config.has_section('Recent'):
            print(config['Recent']['lastfile'])
            last_index = config['Recent']['last_index']
            print(f"last index: {last_index}")
            self.sf_combo.set_active(int(last_index))
            jack_used = config['Recent']['jack_used']
            print(f"jack used: {jack_used}")
            if jack_used == "True":
                self.check_jack.set_active(True)
            else:
                self.check_jack.set_active(False)
                
            
    def handle_close(self, *args):
        self.write_config()
        Gtk.main_quit()
            
            
    

application = MainWindow()
Gtk.main()
