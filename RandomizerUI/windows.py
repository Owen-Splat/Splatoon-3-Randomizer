from PySide6.QtWidgets import QMainWindow, QCheckBox
from RandomizerUI.ui import Ui_MainWindow, Ui_ProgressWindow
from RandomizerUI.settings_manager import SettingsManager
from RandomizerCore.Randomizers.hero import HeroMode_Process
from randomizer_paths import *
from pathlib import Path
import random, shutil

with open(RESOURCE_PATH / 'adjectives.txt', 'r') as f:
    ADJECTIVES = f.read().splitlines()

with open(RESOURCE_PATH / 'characters.txt', 'r') as f:
    CHARACTERS = f.read().splitlines()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.addOptionDescriptions()

        self.settings = SettingsManager(self)
        if not self.settings.load():
            self.ui.showChangelog()


    def browseButtonClicked(self, line_name: str) -> None:
        line = self.ui.findLineEdit(line_name)
        dir = line.text()
        if not Path(dir).exists():
            dir = ''
        folder_path = self.ui.openFileBrowser(dir)
        if folder_path == "": # dont override any existing path if the user canceled the file browser
            return
        line.setText(str(Path(folder_path)))


    def seedButtonClicked(self) -> None:
        adj1 = random.choice(ADJECTIVES)
        adj2 = random.choice(ADJECTIVES)
        char = random.choice(CHARACTERS)
        line = self.ui.findLineEdit("SeedLine")
        line.setText(adj1 + adj2 + char)


    def randomizeButtonClicked(self) -> None:
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

        settings = self.settings.fetch()
        self.progress_window = ProgressWindow(f"{self.windowTitle().split(' v')[0]} - {settings['Seed']}", settings)
        self.progress_window.show()


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


    def validateRomFS(self, line_name: str) -> bool:
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


    def closeEvent(self, event) -> None:
        self.settings.save()
        event.accept()



class ProgressWindow(QMainWindow):
    def __init__(self, title: str, settings: dict) -> None:
        super(ProgressWindow, self).__init__()
        self.ui = Ui_ProgressWindow()
        self.ui.setupUi(title, self)

        self.done = False
        self.cancel = False
        self.mods_error = False
        self.mods_done = False
        self.settings = settings
        self.randomize_hm = False
        self.randomize_so = False

        # remove any old files if generating a new one with the same seed
        self.base_out_dir = Path(str(settings['Output']).split(settings['Seed'])[0] + settings['Seed'])
        if self.base_out_dir.exists():
            shutil.rmtree(str(self.base_out_dir), ignore_errors=True)

        # start mod threads for each mode that the user has selected options for
        if any([v for k,v in settings['HeroMode'].items()]):
            self.randomize_hm = True
            self.mods_process = HeroMode_Process(self, settings)
            self.startModProcess()


    def startModProcess(self) -> None:
        self.mods_process.status_update.connect(self.updateStatus)
        self.mods_process.error.connect(self.modsError)
        self.mods_process.is_done.connect(self.modsDone)
        self.mods_process.start() # start the work thread


    # receives the string signal as a parameter named status
    def updateStatus(self, status: str) -> None:
        self.ui.label.setText(status)


    def modsError(self, er_message=str) -> None:
        self.mods_error = True
        from randomizer_paths import LOGS_PATH
        with open(LOGS_PATH, 'w') as f:
            f.write(f'{self.settings['Seed']}')
            f.write(f'\n\n{er_message}')


    def modsDone(self) -> None:
        if self.mods_error:
            self.updateStatus("Error detected! Check the created log.txt for more info")
            if self.base_out_dir.exists(): # delete files if user canceled
                shutil.rmtree(str(self.base_out_dir), ignore_errors=True)
            self.done = True
            self.ui.progress_bar.hide()
            self.ui.close_button.show()
            return
        
        if self.cancel:
            self.updateStatus("Canceling...")
            if self.base_out_dir.exists(): # delete files if user canceled
                shutil.rmtree(str(self.base_out_dir), ignore_errors=True)
            self.done = True
            self.close()
            return

        if isinstance(self.mods_process, HeroMode_Process) and self.randomize_so:
            pass # will start side order process once it's created
        else:
            self.updateStatus("All done! Check the README for instructions on how to play!")
            self.ui.progress_bar.hide()
            self.ui.folder_button.show()
            self.done = True


    # override the window close event to close the randomization thread
    def closeEvent(self, event) -> None:
        if self.done:
            event.accept()
        else:
            event.ignore()
            self.cancel = True
            self.ui.label.setText('Canceling...')
            self.mods_process.stop()


    def openFolder(self, path):
        if platform.system() == "Windows":
            import os
            os.startfile(path)
        elif platform.system() == "Darwin":
            import subprocess
            subprocess.Popen(["open", path])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", path])


    def openOutputFolderButtonClicked(self):
        self.openFolder(self.base_out_dir.parent.absolute())
        self.window().close()
