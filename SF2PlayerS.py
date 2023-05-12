#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################################
import os
import sys
from PyQt5.QtCore import (QSettings, QProcess, QSize, Qt)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, 
                             QLabel, QComboBox, QCheckBox, QMessageBox, 
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton)

myCompany = "SF2Player"
myApp = "SF2Player"
#####################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.name_list = []
        self.path_list = []
        self.sf2_folder = ""
        
        self.cmd_stop = "killall fluidsynth"
        self.is_running = False
        self.process = QProcess()

        self.w_dir = os.path.dirname(sys.argv[0])        
        os.chdir(self.w_dir)
        
        self.setWindowIcon(QIcon("piano.png"))

        self.sf2_file = ''
        self.isModified = False
        self.settings = QSettings(myCompany, myApp)
        
        self.tb = self.addToolBar("File")
        self.tb.layout().setSpacing(10)
        self.tb.layout().setContentsMargins(10, 10, 10, 10)
        self.tb.setIconSize(QSize(16, 16))
        self.tb.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tb.setMovable(False)
        self.tb.setAllowedAreas(Qt.TopToolBarArea)
        
        self.btn_open = QPushButton(QIcon.fromTheme("document-open"), "")
        self.btn_open.setFlat(True)
        self.btn_open.setToolTip("choose Soundfont Folder")
        self.btn_open.clicked.connect(self.load_sf2)
        self.tb.addWidget(self.btn_open)
        
        self.btn_about = QPushButton(QIcon.fromTheme("help-about"), "")
        self.btn_about.setFlat(True)
        self.btn_about.setToolTip("about SF2Player")
        self.btn_about.clicked.connect(self.about)
        self.tb.addWidget(self.btn_about)

        self.cwid = QWidget()
        hbox = QHBoxLayout()
        btn_box = QHBoxLayout()
        
        sf_lbl = QLabel("<b style='color: #241f31;'>Soundfont:</b>")
        sf_lbl.setFixedSize(75, 30)
        hbox.addWidget(sf_lbl)
        
        self.path_label = QLabel("Soundfont Path")
        self.path_label.setFixedHeight(60)
        #self.path_label.setAlignment(Qt.AlignLeft)
        self.path_label.setWordWrap(True)
        hbox.addWidget(self.path_label)
        
        self.combo_sf2 = QComboBox()
        self.combo_sf2.setStyleSheet("QComboBox {font-size: 8pt; selection-background-color: #729fcf; selection-color: #eee;}")
        self.combo_sf2.setFixedSize(250, 26)
        self.combo_sf2.currentIndexChanged.connect(self.set_from_combo)
        self.combo_sf2.addItem("... choose Soundfont")
        self.tb.addWidget(self.combo_sf2)
        
        # checkbox
        self.check_box = QCheckBox("use jack")
        self.check_box.stateChanged.connect(self.change_state)
        self.tb.addWidget(self.check_box)
        
        self.btn_start = QPushButton("Start")
        self.btn_start.setStyleSheet("QPushButton {background: #deddda;} :hover {background: #729fcf;}")
        self.btn_start.setFixedSize(100, 50)
        btn_icon = QIcon("piano.png")
        self.btn_start.setIcon(btn_icon)
        self.btn_start.setIconSize(QSize(48, 48))
        self.btn_start.clicked.connect(self.start_playing)
        
        btn_box.addWidget(self.btn_start)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(btn_box)
        
        self.cwid.setLayout(vbox)
        self.setCentralWidget(self.cwid)

        self.createStatusBar()
        
        self.check_box.setCheckState(2)
        
        self.change_state()
            
        self.readSettings()
        self.setWindowTitle(myApp)

        
    def change_state(self):
        state = self.check_box.checkState()
        if state == 2:
            self.cmd_start = ('--server --no-shell -p "mysynth" --audio-driver=jack --connect-jack-outputs --reverb=20 --chorus=0 --gain=1.3 -o midi.autoconnect=true  &>/tmp/fluidsynth.out').split(" ")
        else:
            self.cmd_start = ('--server --no-shell -p "mysynth" --audio-driver=pulseaudio --reverb=20 --chorus=0 --gain=1.3 -o midi.autoconnect=true  &>/tmp/fluidsynth.out').split(" ")
        print("state:", state)
        
    def set_from_combo(self):
        ind = self.combo_sf2.currentIndex()
        #print("index:", ind)
        if ind >= 1:
            sf2_path = self.path_list[ind - 1]
            self.path_label.setText(f"<i style='color: #1a5fb4;'>{sf2_path}</i>")
            self.sf2_file = self.path_list[ind - 1]  
            self.cmd_start[11] = self.sf2_file      
        
    def load_sf2(self):
        sf2_folder = QFileDialog.getExistingDirectory(self, "Open Folder", os.path.dirname(self.sf2_folder), QFileDialog.                                               ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if sf2_folder:
            print(sf2_folder)
            self.sf2_folder = sf2_folder
            self.name_list = []
            self.path_list = []
            for root, dirs, files in os.walk(sf2_folder, topdown = False):
               for name in files:
                  if name.endswith(".sf2"):
                      self.path_list.append(os.path.join(root, name))
                      self.combo_sf2.addItem(name)            
        
    def start_playing(self):
        self.change_state()
        if not self.sf2_file == "":
            self.cmd_start[11] = self.sf2_file
            if self.btn_start.text() == "Start":
                self.tb.setVisible(False)
                self.btn_start.setText("Stop")
                self.btn_start.setIcon(QIcon("piano_stop.png"))
                print("fluidsynth", " ".join(self.cmd_start))
                self.statusBar().showMessage("Server started")
                self.is_running = True
                self.process.start("fluidsynth", self.cmd_start)
                print(f"Process-ID: {self.process.processId()}")
                self.check_box.setVisible(False)
            else:
                self.btn_start.setText("Start")
                self.btn_start.setIcon(QIcon("piano.png"))
                self.process.kill()
                self.tb.setVisible(True)
                self.statusBar().showMessage("Server stopped")
                self.is_running = False
                self.check_box.setVisible(True)
        else:
            print("no soundfont")
            self.statusBar().showMessage("no soundfont")

    def closeEvent(self, event):
        if self.is_running:
            self.process.kill()
        self.writeSettings()
        event.accept()

    def createStatusBar(self):
        self.statusBar().setStyleSheet("font-size: 8pt; color: #888a85;")
        self.statusBar().showMessage("Ready")

    def readSettings(self):
        if self.settings.contains("pos"):
            pos = self.settings.value("pos")
            self.move(pos)
        if self.settings.contains("size"):
            size = self.settings.value("size")
            self.resize(size)
        if self.settings.contains("sf2"):
            sf2_path = self.settings.value("sf2")
            self.sf2_file = sf2_path
            self.path_label.setText(f"<i style='color: #1a5fb4;'>{sf2_path}</i>")
            self.cmd_start[11] = self.sf2_file
            self.statusBar().showMessage(f"{os.path.basename(self.sf2_file)} loaded")
        if self.settings.contains("sf2_folder"):
            self.sf2_folder = self.settings.value("sf2_folder")            
            for root, dirs, files in os.walk(self.sf2_folder, topdown = False):
               for name in files:
                  if name.endswith(".sf2"):
                      self.path_list.append(os.path.join(root, name))
                      self.combo_sf2.addItem(name) 
                      
    def writeSettings(self):
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("size", self.size())
        if not self.sf2_file == "":
            self.settings.setValue("sf2", self.sf2_file)            
        if not self.sf2_folder == "":
            self.settings.setValue("sf2_folder", self.sf2_folder)
        
    def about(self):
        link = "<a title='Axel Schneider' href='https://github.com/Axel-Erfurt' target='_blank'>Axel Schneider</a>"
        title = "about SF2Player"
        message = f'<br><h2>SF2Player 1.0</h2><h4 style="color: #1a5fb4;">Fluidsynth Player</h4>created with PyQt5 by {link}<br><br>©2022<br>Copyright © 2022 The Qt Company Ltd and other contributors.<br>Qt and the Qt logo are trademarks of The Qt Company Ltd.'
        self.msgbox(title, message)

    def msgbox(self, title, message):
        msg = QMessageBox(1, title, message, QMessageBox.Ok)
        msg.exec()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
