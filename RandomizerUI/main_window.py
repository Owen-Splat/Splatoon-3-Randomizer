from PySide6.QtWidgets import QMainWindow, QCheckBox
# from RandomizerUI.UI.ui_form import Ui_MainWindow
from RandomizerUI.ui import Ui_MainWindow
# from RandomizerUI.progress_window import ProgressWindow
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

        if DEFAULTS:
            self.ui.showChangelog()
        else:
            settings_manager.loadSettings(self, SETTINGS)


    def browseButtonClicked(self, line_name: str) -> None:
        line = self.ui.findLineEdit(line_name)
        dir = line.text()
        if not Path(dir).exists():
            dir = ''
        folder_path = self.ui.openFileBrowser(dir)
        if folder_path == "": # dont override any existing path if the user canceled the file browser
            return
        line.setText(str(Path(folder_path)))


    def seedButtonClicked(self):
        adj1 = random.choice(ADJECTIVES)
        adj2 = random.choice(ADJECTIVES)
        char = random.choice(CHARACTERS)
        line = self.ui.findLineEdit("SeedLine")
        line.setText(adj1 + adj2 + char)


    def randomizeButtonClicked(self):
        # first we need to check all settings under each tab
        # if all of them are unchecked, skip over randomizing that mode
        hm_tab = self.ui.findTab("HeroModeTab")
        randomize_hm: bool = any([c.isChecked() for c in hm_tab.findChildren(QCheckBox)])
        so_tab = self.ui.findTab("SideOrderTab")
        randomize_so: bool = any([c.isChecked() for c in so_tab.findChildren(QCheckBox)]) # False until we add settings

        if not randomize_hm and not randomize_so:
            self.ui.showUserError("You need to select some settings first!")
            return

        if not self.validateFolders(randomize_hm, randomize_so):
            return

        seed = self.ui.findLineEdit("SeedLine").text().strip()
        if seed:
            if len(seed) > 50:
                seed = seed[:50]
        else:
            random.seed()
            seed = str(random.getrandbits(32))

        outdir = f"{self.ui.findLineEdit("OutLine").text()}/{seed}"
        if self.ui.findComboBox("PlatformBox").currentText()[9:].strip() == 'Console':
            outdir += '/atmosphere/contents/0100C2500FC20000'
        outdir += '/romfs'

        major_version = self.ui.findSpinBox("MajorVersion").value()
        minor_version = self.ui.findSpinBox("MinorVersion").value()
        patch_version = self.ui.findSpinBox("PatchVersion").value()

        settings = {
            'RomFS': self.ui.findLineEdit("BaseLine").text(),
            # 'DLC': self.ui.findLineEdit("DLCLine").text(),
            'Output': outdir,
            'Seed': seed,
            'Version': f"{major_version}.{minor_version}.{patch_version}",
            'HeroMode': {},
            'SideOrder': {},
        }
        for c in hm_tab.findChildren(QCheckBox):
            settings['HeroMode'][c.text()] = c.isChecked()
        for c in so_tab.findChildren(QCheckBox):
            settings['SideOrder'][c.text()] = c.isChecked()

        print("Would open ProgressWindow")
        # self.progress_window = ProgressWindow(settings)
        # self.progress_window.setWindowTitle(f"{self.windowTitle().split(' v')[0]} - {seed}")
        # self.progress_window.show()


    def validateFolders(self, base: bool, dlc: bool) -> bool:
        """Validates the necessary paths depending on if the user wants to randomize specific modes"""

        if dlc: # Side Order needs to modify the base RomFS too, so check base path regardless
            base = True

        if base and not self.validateRomFS("BaseLine"):
            return False

        if dlc and not self.validateRomFS("DLCLine"):
            return False

        if not Path(self.ui.findLineEdit("OutLine").text()).exists():
            self.ui.showUserError('Output path does not exist!')
            return False

        return True


    def validateRomFS(self, line_name: str):
        line = self.ui.findLineEdit(line_name)
        romfs_path = Path(line.text())
        field = ""
        level_prefix = ""
        match line_name:
            case "BaseLine":
                field = "RomFS Path"
                level_prefix = "Msn_"
            case "DLCLine":
                field = "DLC Path"
                level_prefix = "Sdodr_"

        if romfs_path == Path():
            self.ui.showUserError(f"{field} is empty!")
            return False
        if not romfs_path.exists():
            self.ui.showUserError(f'{field} does not exist!\n\n"{line.text()}"')
            return False

        if (romfs_path / 'romfs').exists():
            romfs_path = romfs_path / 'romfs'
            line.setText(str(romfs_path))

        # validate the romfs by checking for Scenes
        try:
            level_files = [f.name for f in (romfs_path / 'Pack' / 'Scene').iterdir() if f.name.startswith(level_prefix)]
            if not level_files:
                self.ui.showUserError(f'Could not find any level files!\n\n"{str(romfs_path)}"')
                return False
        except FileNotFoundError as e:
            self.ui.showUserError(f'Could not validate RomFS:\n\n{e}')
            return False

        return True


    def closeEvent(self, event):
        settings_manager.saveSettings(self)
        event.accept()
