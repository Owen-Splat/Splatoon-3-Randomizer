from RandomizerCore.Data.randomizer_data import *
import yaml, os

MAIN_ORDERS = {
    'kettleCheck': True,
    'lavaCheck': False,
    'cutsceneCheck': True,
    'backgroundCheck': False,
    'inkCheck': True,
    'musicCheck': True,
    'gearCheck': False,
    'oozeCheck': False,
    'collectCheck': True
}
SIDE_ORDERS = {

}
ALL_ORDERS = {**MAIN_ORDERS, **SIDE_ORDERS}


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


def saveSettings(window):
    seed = window.ui.lineEdit_4.text()
    if len(seed) > 50:
        seed = seed[:50]
    
    settings_dict = {
        'RomFS_Folder': window.ui.lineEdit.text(),
        'DLC_Folder': window.ui.lineEdit_2.text(),
        'Output_Folder': window.ui.lineEdit_3.text(),
        'Seed': seed,
        'Platform': window.ui.platformComboBox.currentText()[10:],
        'Season': window.ui.seasonSpinBox.value(),
        'Return of the Mammalians': {},
        'Spire of Order': {}
    }

    ldict = locals()
    for k,v in MAIN_ORDERS.items():
        exec(f"v = window.ui.{k}.isChecked()", globals(), ldict)
        exec(f"k = window.ui.{k}.text()", globals(), ldict)
        settings_dict['Return of the Mammalians'][ldict['k']] = ldict['v']
    for k,v in SIDE_ORDERS.items():
        exec(f"v = window.ui.{k}.isChecked()", globals(), ldict)
        exec(f"k = window.ui.{k}.text()", globals(), ldict)
        settings_dict['Spire of Order'][ldict['k']] = ldict['v']
    
    with open(SETTINGS_PATH, 'w') as settingsFile:
        yaml.dump(settings_dict, settingsFile, Dumper=MyDumper, sort_keys=False)


def loadSettings(window, settings, checks):
    for k,v in settings.items():
        if isinstance(v, dict):
            for k,v in v.items():
                check = [c for c,x in checks.items() if x == k][0]
                exec(f"window.ui.{check}.setChecked({v})")
        else:
            if not isinstance(v, bool):
                continue
            check = [c for c,x in checks.items() if x == k][0]
            exec(f"window.ui.{check}.setChecked({v})")

    if 'RomFS_Folder' in settings:
        if os.path.exists(settings['RomFS_Folder']):
            window.ui.lineEdit.setText(settings['RomFS_Folder'])
    if 'DLC_Folder' in settings:
        if os.path.exists(settings['DLC_Folder']):
            window.ui.lineEdit_2.setText(settings['DLC_Folder'])
    if 'Output_Folder' in settings:
        if os.path.exists(settings['Output_Folder']):
            window.ui.lineEdit_3.setText(settings['Output_Folder'])
    if 'Seed' in settings:
        window.ui.lineEdit_4.setText(settings['Seed'])
    if 'Platform' in settings:
        window.ui.platformComboBox.setCurrentIndex(1 if str(settings['Platform']).lower().strip() == 'emulator' else 0)
    if 'Season' in settings:
        if isinstance(settings['Season'], int):
            window.ui.seasonSpinBox.setValue(settings['Season'])