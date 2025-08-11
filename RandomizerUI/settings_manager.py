from PySide6.QtWidgets import QCheckBox
from randomizer_data import *
from pathlib import Path
import yaml


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


def saveSettings(window) -> None:
    seed = window.ui.findLineEdit("SeedLine").text()
    if len(seed) > 32:
        seed = seed[:32]

    major_version = window.ui.findSpinBox("MajorVersion").value()
    minor_version = window.ui.findSpinBox("MinorVersion").value()
    patch_version = window.ui.findSpinBox("PatchVersion").value()

    settings = {
        'RomFS': window.ui.findLineEdit("BaseLine").text(),
        # 'DLC': window.ui.findLineEdit("DLCLine").text(),
        'Output': window.ui.findLineEdit("OutLine").text(),
        'Seed': seed,
        'Version': f"{major_version}.{minor_version}.{patch_version}",
        'Platform': window.ui.findComboBox("PlatformBox").currentText()[9:].strip(),
        'HeroMode': {},
        # 'SideOrder': {}
    }

    hm_tab = window.ui.findTab("HeroModeTab")
    for c in hm_tab.findChildren(QCheckBox):
        settings['HeroMode'][c.text()] = c.isChecked()

    so_tab = window.ui.findTab("SideOrderTab")
    for c in so_tab.findChildren(QCheckBox):
        settings['SideOrder'][c.text()] = c.isChecked()
    
    with open(SETTINGS_PATH, 'w') as f:
        yaml.dump(settings, f, Dumper=MyDumper, sort_keys=False)


def loadSettings(window, settings) -> None:
    for k,v in settings.items():
        if isinstance(v, dict):
            for k,v in v.items():
                window.ui.findCheckBox(k).setChecked(v)
        else:
            if not isinstance(v, bool):
                try:
                    match k:
                        case 'RomFS':
                            romfs_path = Path(settings[k])
                            if romfs_path != Path() and romfs_path.exists():
                                window.ui.findLineEdit("BaseLine").setText(settings[k])
                        case 'DLC':
                            dlc_path = Path(settings[k])
                            if dlc_path != Path() and dlc_path.exists():
                                window.ui.findLineEdit("DLCLine").setText(settings[k])
                        case 'Output':
                            out_path = Path(settings[k])
                            if out_path != Path() and out_path.exists():
                                window.ui.findLineEdit("OutLine").setText(settings[k])
                        case 'Seed':
                            seed = str(settings[k])
                            if len(seed) > 32:
                                seed = seed[:32]
                            window.ui.findLineEdit("SeedLine").setText(seed)
                        case 'Platform':
                            window.ui.findComboBox("PlatformBox").setCurrentIndex(
                                1 if str(settings[k]).lower().strip() == 'emulator' else 0)
                        case 'Version':
                            game_version = str(settings[k]).split('.')
                            major_version = int(game_version[0])
                            minor_version = int(game_version[1])
                            patch_version = int(game_version[2])
                            window.ui.findSpinBox("MajorVersion").setValue(major_version)
                            window.ui.findSpinBox("MinorVersion").setValue(minor_version)
                            window.ui.findSpinBox("PatchVersion").setValue(patch_version)
                except: # if it errors we dont really care why, ignore so it is left at the default value
                    continue
            else:
                window.ui.findCheckBox(k).setChecked(v)
