from PySide6.QtWidgets import QCheckBox
from randomizer_paths import SETTINGS_PATH
from pathlib import Path
import random, yaml


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


class SettingsManager:
    """A class for managing user settings"""

    def __init__(self, window) -> None:
        self.window = window
        self.saving = False


    def save(self) -> None:
        """Saves the current settings to a file"""

        self.saving = True
        with open(SETTINGS_PATH, 'w') as f:
            yaml.dump(self.fetch(), f, Dumper=MyDumper, sort_keys=False)
        self.saving = False


    def load(self) -> bool:
        """Loads settings from a file. Returns if successful"""

        try:
            with open(SETTINGS_PATH, 'r') as f:
                settings = yaml.safe_load(f)
        except FileNotFoundError:
            return False

        for k,v in settings.items():
            if isinstance(v, dict):
                for k,v in v.items():
                    check = self.window.ui.findCheckBox(k)
                    if check is None:
                        continue
                    self.window.ui.findCheckBox(k).setChecked(v)
            else:
                if not isinstance(v, bool):
                    try:
                        match k:
                            case 'RomFS':
                                romfs_path = Path(settings[k])
                                if romfs_path != Path() and romfs_path.exists():
                                    self.window.ui.findLineEdit("BaseLine").setText(settings[k])
                            case 'DLC':
                                dlc_path = Path(settings[k])
                                if dlc_path != Path() and dlc_path.exists():
                                    self.window.ui.findLineEdit("DLCLine").setText(settings[k])
                            case 'Output':
                                out_path = Path(settings[k])
                                if out_path != Path() and out_path.exists():
                                    self.window.ui.findLineEdit("OutLine").setText(settings[k])
                            case 'Seed':
                                seed = str(settings[k])
                                if len(seed) > 32:
                                    seed = seed[:32]
                                self.window.ui.findLineEdit("SeedLine").setText(seed)
                            case 'Platform':
                                self.window.ui.findComboBox("PlatformBox").setCurrentIndex(
                                    1 if str(settings[k]).lower().strip() == 'emulator' else 0)
                    except: # if it errors we dont really care why, ignore so it is left at the default value
                        continue
                else:
                    self.window.ui.findCheckBox(k).setChecked(v)

        return True


    def fetch(self) -> dict:
        """Fetches the current user settings"""

        seed = self.window.ui.findLineEdit("SeedLine").text()
        if len(seed) > 32:
            seed = seed[:32]
        else:
            if not self.saving:
                random.seed()
                seed = str(random.getrandbits(32))

        outdir = self.window.ui.findLineEdit("OutLine").text()
        if not self.saving:
            outdir = Path(outdir) / f"S3Rando-{seed}"
            if self.window.ui.findComboBox("PlatformBox").currentText()[9:].strip() == 'Console':
                outdir = outdir / 'atmosphere' / 'contents' / '0100C2500FC20000'
            outdir = outdir / 'romfs'

        settings = {
            'RomFS': self.window.ui.findLineEdit("BaseLine").text(),
            # 'DLC': window.ui.findLineEdit("DLCLine").text(),
            'Output': outdir,
            'Seed': seed,
            'Platform': self.window.ui.findComboBox("PlatformBox").currentText()[9:].strip(),
            'HeroMode': {},
            # 'SideOrder': {}
        }

        hm_tab = self.window.ui.findTab("HeroModeTab")
        for c in hm_tab.findChildren(QCheckBox):
            settings['HeroMode'][c.text()] = c.isChecked()

        so_tab = self.window.ui.findTab("SideOrderTab")
        for c in so_tab.findChildren(QCheckBox):
            settings['SideOrder'][c.text()] = c.isChecked()

        return settings
