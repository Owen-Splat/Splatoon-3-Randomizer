import os
import sys
import appdirs

if getattr(sys, "frozen", False):
    RUNNING_FROM_SOURCE = False
    ROOT_PATH = os.path.dirname(sys.executable)
    if sys.platform == 'darwin': # mac
        userdata_path = appdirs.user_data_dir('randomizer', 'Splatoon 3 Randomizer')
        if not os.path.isdir(userdata_path):
            os.mkdir(userdata_path)
        SETTINGS_PATH = os.path.join(userdata_path, 'settings.txt')
        LOGS_PATH = os.path.join(userdata_path, 'log.txt')
    else:
        SETTINGS_PATH = os.path.join('.', 'settings.txt')
        LOGS_PATH = os.path.join('.', 'log.txt')
else:
    RUNNING_FROM_SOURCE = True
    ROOT_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
    SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings.txt')
    LOGS_PATH = os.path.join(ROOT_PATH, 'log.txt')

DATA_PATH = os.path.join(ROOT_PATH, 'RandomizerCore/Data')
RESOURCE_PATH = os.path.join(ROOT_PATH, 'RandomizerCore/Resources')
