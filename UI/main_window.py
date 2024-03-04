from PySide6 import QtCore, QtWidgets
from UI.ui_form import Ui_MainWindow
from UI.progress_window import ProgressWindow

from randomizer_data import *
from randomizer_paths import *

import os
import yaml
import random



class MyDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)



class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super (MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # randomizer settings connections
        self.ui.browseButton1.clicked.connect(self.romBrowse)
        self.ui.browseButton2.clicked.connect(self.dlcBrowse)
        self.ui.browseButton3.clicked.connect(self.outBrowse)
        self.ui.seedButton.clicked.connect(self.generateSeed)
        self.ui.randomizeButton.clicked.connect(self.randomizeButton_Clicked)
                
        desc_items = self.ui.tab.findChildren(QtWidgets.QCheckBox)
        for item in desc_items:
            item.installEventFilter(self)
        
        if DEFAULTS:
            for item in desc_items:
                item.setChecked(True)
            self.ui.lavaCheck.setChecked(False)
            self.ui.backgroundCheck.setChecked(False)
            self.ui.oozeCheck.setChecked(False)
        else:
            self.loadSettings()
        
        self.setFixedSize(780, 400)
        self.setWindowTitle(f'{self.windowTitle()} v{VERSION}')
        self.show()


    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Type.HoverEnter:
            self.ui.explainLabel.setText(source.whatsThis())
            self.ui.explainLabel.setStyleSheet('color: black;')
        
        elif event.type() == QtCore.QEvent.Type.HoverLeave:
            self.ui.explainLabel.setText('Hover over an option to see what it does')
            self.ui.explainLabel.setStyleSheet('color: rgb(80, 80, 80);')
        
        return QtWidgets.QWidget.eventFilter(self, source, event)


    def saveSettings(self):
        settings_dict = {
            'Romfs_Folder': self.ui.lineEdit.text(),
            'DLC_Folder': self.ui.lineEdit_2.text(),
            'Output_Folder': self.ui.lineEdit_3.text(),
            'Seed': self.ui.lineEdit_4.text(),
            'Platform': self.ui.platformComboBox.currentText(),
            'Season': self.ui.seasonSpinBox.value(),
            'Kettles': self.ui.kettleCheck.isChecked(),
            # 'Beatable': self.ui.beatableCheck.isChecked(),
            'Backgrounds': self.ui.backgroundCheck.isChecked(),
            'Hero_Gear': self.ui.gearCheck.isChecked(),
            '1HKO': self.ui.lavaCheck.isChecked(),
            'Ink_Color': self.ui.inkCheck.isChecked(),
            'Music': self.ui.musicCheck.isChecked(),
            'Skip_Cutscenes': self.ui.cutsceneCheck.isChecked(),
            'Fuzzy_Ooze_Costs': self.ui.oozeCheck.isChecked(),
            'Collectables': self.ui.collectCheck.isChecked()
        }
        
        with open(SETTINGS_PATH, 'w') as settingsFile:
            yaml.dump(settings_dict, settingsFile, Dumper=MyDumper, sort_keys=False)


    def loadSettings(self):
        try:
            if os.path.exists(SETTINGS['Romfs_Folder']):
                self.ui.lineEdit.setText(SETTINGS['Romfs_Folder'])
        except (KeyError, TypeError):
            pass
        
        try:
            if os.path.exists(SETTINGS['DLC_Folder']):
                self.ui.lineEdit_2.setText(SETTINGS['DLC_Folder'])
        except (KeyError, TypeError):
            pass

        try:
            if os.path.exists(SETTINGS['Output_Folder']):
                self.ui.lineEdit_3.setText(SETTINGS['Output_Folder'])
        except (KeyError, TypeError):
            pass
        
        try:
            if SETTINGS['Seed'] != "":
                self.ui.lineEdit_4.setText(SETTINGS['Seed'])
        except (KeyError, TypeError):
            pass

        try:
            self.ui.platformComboBox.setCurrentIndex(1 if str(SETTINGS['Platform']).lower().strip() == 'emulator' else 0)
        except (KeyError, TypeError):
            pass

        try:
            self.ui.seasonSpinBox.setValue(int(SETTINGS['Season']))
        except (KeyError, TypeError, ValueError):
            pass

        try:
            self.ui.kettleCheck.setChecked(SETTINGS['Kettles'])
        except(KeyError, TypeError):
            self.ui.kettleCheck.setChecked(True)
        
        # try:
        #     self.ui.beatableCheck.setChecked(SETTINGS['Beatable'])
        # except(KeyError, TypeError):
        #     self.ui.beatableCheck.setChecked(True)
        
        try:
            self.ui.backgroundCheck.setChecked(SETTINGS['Backgrounds'])
        except(KeyError, TypeError):
            self.ui.backgroundCheck.setChecked(False)
        
        try:
            self.ui.gearCheck.setChecked(SETTINGS['Hero_Gear'])
        except(KeyError, TypeError):
            self.ui.gearCheck.setChecked(True)
        
        try:
            self.ui.lavaCheck.setChecked(SETTINGS['1HKO'])
        except(KeyError, TypeError):
            self.ui.lavaCheck.setChecked(False)

        try:
            self.ui.inkCheck.setChecked(SETTINGS['Ink_Color'])
        except(KeyError, TypeError):
            self.ui.inkCheck.setChecked(True)

        try:
            self.ui.musicCheck.setChecked(SETTINGS['Music'])
        except(KeyError, TypeError):
            self.ui.musicCheck.setChecked(True)
        
        try:
            self.ui.cutsceneCheck.setChecked(SETTINGS['Skip_Cutscenes'])
        except(KeyError, TypeError):
            self.ui.cutsceneCheck.setChecked(True)
        
        try:
            self.ui.oozeCheck.setChecked(SETTINGS['Fuzzy_Ooze_Costs'])
        except(KeyError, TypeError):
            self.ui.oozeCheck.setChecked(False)
        
        try:
            self.ui.collectCheck.setChecked(SETTINGS['Collectables'])
        except(KeyError, TypeError):
            self.ui.collectCheck.setChecked(True)
    
    
    # RomFS Folder Browse
    def romBrowse(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.path.exists(folder_path):
            self.ui.lineEdit.setText(folder_path)
    
    
    def dlcBrowse(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.path.exists(folder_path):
            self.ui.lineEdit_2.setText(folder_path)
    
    
    # Output Folder Browse
    def outBrowse(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.path.exists(folder_path):
            self.ui.lineEdit_3.setText(folder_path)
    
    
    # Generate New Seed
    def generateSeed(self):
        adj1 = random.choice(ADJECTIVES)
        adj2 = random.choice(ADJECTIVES)
        char = random.choice(CHARACTERS)
        self.ui.lineEdit_4.setText(adj1 + adj2 + char)
    

    def validateFolders(self) -> bool:
        rom_path = self.ui.lineEdit.text()
        
        if not os.path.exists(rom_path):
            self.showUserError('RomFS path does not exist!')
            return False
        
        # get the right folder
        folders = [f.lower() for f in os.listdir(rom_path)]
        if 'pack' in folders:
            pass
        elif 'romfs' in folders:
            rom_path = os.path.join(rom_path, 'romfs')
            self.ui.lineEdit.setText(rom_path)
        else:
            self.showUserError('RomFS path is not valid!')
            return False
        
        # validate the romfs by checking how many missions the user has in their romfs
        try:
            level_files = [f for f in os.listdir(f'{rom_path}/Pack/Scene') if f.startswith('Msn_')]
            if len(level_files) < 69:
                self.showUserError('Could not find all level files')
                return False
        except FileNotFoundError as e:
            self.showUserError(f'Could not validate RomFS:\n\n{e}')
            return False

        if not os.path.exists(self.ui.lineEdit_3.text()):
            self.showUserError('Output path does not exist!')
            return False
        
        return True
    
    
    # Randomize Button Clicked
    def randomizeButton_Clicked(self):
        if not self.validateFolders():
            return
        
        seed = self.ui.lineEdit_3.text().strip()
        if seed == '':
            random.seed()
            seed = str(random.getrandbits(32))
        
        outdir = f"{self.ui.lineEdit_2.text()}/{seed}"
        if self.ui.platformComboBox.currentText() == 'Platform: Console':
            outdir += '/atmosphere/contents/0100C2500FC20000'
        outdir += '/romfs'
        
        settings = {
            'season': self.ui.seasonSpinBox.value(),
            'kettles': self.ui.kettleCheck.isChecked(),
            # 'beatable': self.ui.beatableCheck.isChecked(),
            'backgrounds': self.ui.backgroundCheck.isChecked(),
            'gear': self.ui.gearCheck.isChecked(),
            '1HKO': self.ui.lavaCheck.isChecked(),
            'ink-color': self.ui.inkCheck.isChecked(),
            'music': self.ui.musicCheck.isChecked(),
            'skip-cutscenes': self.ui.cutsceneCheck.isChecked(),
            'ooze-costs': self.ui.oozeCheck.isChecked(),
            'collectables': self.ui.collectCheck.isChecked()
        }
        
        self.progress_window = ProgressWindow(self.ui.lineEdit.text(), outdir, seed, settings)
        self.progress_window.setFixedSize(472, 125)
        self.progress_window.setWindowTitle(f"{seed}")
        self.progress_window.show()


    # def pickCustomColor(self):
    #     dlg = QtWidgets.QColorDialog()
    #     if dlg.exec_():
    #         self.ui.colorButton.setStyleSheet(f'background-color: {dlg.currentColor().name()};')


    def showUserError(self, msg):
        message = QtWidgets.QMessageBox()
        message.setWindowTitle('Error')
        message.setText(msg)
        message.exec()


    def closeEvent(self, event):
        self.saveSettings()
        event.accept()
