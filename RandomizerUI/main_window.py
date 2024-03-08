from PySide6 import QtCore, QtWidgets
from RandomizerUI.UI.ui_form import Ui_MainWindow
from RandomizerUI.progress_window import ProgressWindow
import RandomizerUI.settings_manager as settings_manager
from RandomizerCore.Data.randomizer_data import *
from RandomizerCore.Paths.randomizer_paths import *
import os, random



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super (MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.browseButton1.clicked.connect(self.romBrowse)
        self.ui.browseButton2.clicked.connect(self.dlcBrowse)
        self.ui.browseButton3.clicked.connect(self.outBrowse)
        self.ui.seedButton.clicked.connect(self.generateSeed)
        self.ui.randomizeButton.clicked.connect(self.randomizeButton_Clicked)
        
        desc_items = self.ui.tab.findChildren(QtWidgets.QCheckBox)
        for item in desc_items:
            item.installEventFilter(self)
        
        if DEFAULTS:
            for k,v in settings_manager.ALL_ORDERS.items():
                exec(f"self.ui.{k}.setChecked({v})")
        else:
            checks = {}
            for option in settings_manager.ALL_ORDERS:
                widget = self.findChild(QtWidgets.QWidget, option)
                checks[option] = widget.text()
            settings_manager.loadSettings(self, SETTINGS, checks)
        
        self.setFixedSize(self.size())
        self.setWindowTitle(f'{self.windowTitle()} v{VERSION}')
        self.show()

        if DEFAULTS or RUNNING_FROM_SOURCE:
            self.showChangeLog()
    
    
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Type.HoverEnter:
            self.ui.explainLabel.setText(source.whatsThis())
            self.ui.explainLabel.setStyleSheet('color: black;')
        
        elif event.type() == QtCore.QEvent.Type.HoverLeave:
            self.ui.explainLabel.setText('Hover over an option to see what it does')
            self.ui.explainLabel.setStyleSheet('color: rgb(80, 80, 80);')
        
        return QtWidgets.QWidget.eventFilter(self, source, event)
    
    
    def romBrowse(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.path.exists(folder_path):
            self.ui.lineEdit.setText(folder_path)
    
    
    def dlcBrowse(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.path.exists(folder_path):
            self.ui.lineEdit_2.setText(folder_path)
    
    
    def outBrowse(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.path.exists(folder_path):
            self.ui.lineEdit_3.setText(folder_path)
    
    
    def generateSeed(self):
        adj1 = random.choice(ADJECTIVES)
        adj2 = random.choice(ADJECTIVES)
        char = random.choice(CHARACTERS)
        self.ui.lineEdit_4.setText(adj1 + adj2 + char)
    
    
    def randomizeButton_Clicked(self):
        if not self.validateFolders():
            return
        
        seed = self.ui.lineEdit_4.text().strip()
        if seed:
            if len(seed) > 50:
                seed = seed[:50]
        else:
            random.seed()
            seed = str(random.getrandbits(32))
        
        outdir = f"{self.ui.lineEdit_3.text()}/{seed}"
        if self.ui.platformComboBox.currentText()[10:] == 'Console':
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
    
    
    def validateFolders(self) -> bool:
        if not self.validateRomFS(self.ui.lineEdit.text()):
            return False
        
        if not self.validateRomFS(self.ui.lineEdit_2.text()):
            return False
        
        if not os.path.exists(self.ui.lineEdit_3.text()):
            self.showUserError('Output path does not exist!')
            return False
        
        return True
    
    
    def validateRomFS(self, romfs_path):
        if not os.path.exists(romfs_path):
            self.showUserError('RomFS path does not exist!')
            return False
        
        # get the right folder
        folders = [f.lower() for f in os.listdir(romfs_path)]
        if 'pack' in folders:
            pass
        elif 'romfs' in folders:
            romfs_path = os.path.join(romfs_path, 'romfs')
            self.ui.lineEdit.setText(romfs_path)
        else:
            self.showUserError('RomFS path is not valid!')
            return False
        
        # validate the romfs by checking for Scenes
        try:
            level_files = [f for f in os.listdir(f'{romfs_path}/Pack/Scene') if f.startswith(('Msn_', 'Sdodr_'))]
            if not level_files:
                self.showUserError('Could not find any level files!')
                return False
        except FileNotFoundError as e:
            self.showUserError(f'Could not validate RomFS:\n\n{e}')
            return False
        
        return True
    
    
    def showUserError(self, msg):
        message = QtWidgets.QMessageBox()
        message.setWindowTitle('Error')
        message.setText(msg)
        message.exec()
    
    
    def showChangeLog(self):
        message = QtWidgets.QMessageBox()
        message.setWindowTitle("What's New?")
        message.setText(CHANGES)
        message.setDetailedText(LOG)
        message.exec()
    
    
    def closeEvent(self, event):
        settings_manager.saveSettings(self)
        event.accept()
