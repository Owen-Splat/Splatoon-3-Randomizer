from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QFileDialog
# from RandomizerUI.UI.ui_form import Ui_MainWindow
from RandomizerUI.ui import Ui_MainWindow
from RandomizerUI.progress_window import ProgressWindow
import RandomizerUI.settings_manager as settings_manager
from RandomizerCore.Data.randomizer_data import *
from randomizer_paths import *
import random


class MainWindow(QMainWindow):
    def __init__(self):
        super (MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.addOptionDescriptions()

        # if DEFAULTS:
        #     for k,v in settings_manager.ALL_ORDERS.items():
        #         exec(f"self.ui.{k}.setChecked({v})")
        # else:
        #     checks = {}
        #     for option in settings_manager.ALL_ORDERS:
        #         widget = self.findChild(QtWidgets.QWidget, option)
        #         checks[option] = widget.text()
        #     settings_manager.loadSettings(self, SETTINGS, checks)

        # self.setFixedSize(self.size())
        # self.setWindowTitle(f'{self.windowTitle()} v{VERSION}')
        # self.show()

        if DEFAULTS or RUNNING_FROM_SOURCE:
            self.ui.showChangelog()


    def browseButtonClicked(self, line_name: str) -> None:
        line = self.ui.findLineEdit(line_name)
        dir = line.text()
        if not Path(dir).exists():
            dir = ''
        folder_path = self.ui.openFileBrowser(dir)
        if folder_path != "" and Path(folder_path).exists():
            line.setText(str(Path(folder_path)))


    def seedButtonClicked(self):
        adj1 = random.choice(ADJECTIVES)
        adj2 = random.choice(ADJECTIVES)
        char = random.choice(CHARACTERS)
        line = self.ui.findLineEdit("SeedLine")
        line.setText(adj1 + adj2 + char)


    def randomizeButtonClicked(self):
        if not self.validateFolders():
            return

        return
        seed = self.ui.findLineEdit("SeedLine").text().strip()
        if seed:
            if len(seed) > 50:
                seed = seed[:50]
        else:
            random.seed()
            seed = str(random.getrandbits(32))

        outdir = f"{self.ui.findLineEdit("OutLine").text()}/{seed}"
        if self.ui.findComboBox("PlatformBox").currentText()[10:] == 'Console':
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
        rotm, sdodr = self.ui.createModeWindow()

        print(rotm, sdodr)
        if not rotm and not sdodr:
            return False

        if not self.validateRomFS("BaseLine"):
            return False

        if sdodr and not self.validateRomFS("DLCLine"):
            return False

        if not Path(self.ui.findLineEdit("OutLine").text()).exists():
            self.ui.showUserError('Output path does not exist!')
            return False

        return True


    def validateRomFS(self, line_name: str):
        line = self.ui.findLineEdit(line_name)
        romfs_path = Path(line.text())

        if not romfs_path.exists() and str(romfs_path) != "":
            self.ui.showUserError(f'RomFS path does not exist!\n\n"{str(romfs_path)}"')
            return False

        if (romfs_path / 'romfs').exists():
            romfs_path = romfs_path / 'romfs'
            line.setText(str(romfs_path))

        # validate the romfs by checking for Scenes
        try:
            level_files = [f.name for f in (romfs_path / 'Pack' / 'Scene').iterdir() if f.startswith(('Msn_', 'Sdodr_'))]
            if not level_files:
                self.ui.showUserError(f'Could not find any level files!\n\n"{str(romfs_path)}"')
                return False
        except FileNotFoundError as e:
            self.ui.showUserError(f'Could not validate RomFS:\n\n{e}')
            return False

        return True


    # def closeEvent(self, event):
    #     settings_manager.saveSettings(self)
    #     event.accept()
