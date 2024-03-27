from RandomizerCore.Paths.randomizer_paths import *

import yaml
import os

VERSION = "0.2.0"

with open(os.path.join(RESOURCE_PATH, 'adjectives.txt'), 'r') as f:
    ADJECTIVES = f.read().splitlines()

with open(os.path.join(RESOURCE_PATH, 'characters.txt'), 'r') as f:
    CHARACTERS = f.read().splitlines()

with open(os.path.join(RESOURCE_PATH, 'changelog.txt'), 'r') as f:
    full_log = f.read()
    logs = full_log.split('------')
    NEW_CHANGES = logs[0]
    logs.pop(0)
    OLD_CHANGES = "".join(logs).strip()

with open(os.path.join(DATA_PATH, 'parameters.yml'), 'r') as f:
    PARAMS = yaml.safe_load(f)

try:
    with open(SETTINGS_PATH, 'r') as f:
        SETTINGS = yaml.safe_load(f)
        DEFAULTS = False
except FileNotFoundError:
    DEFAULTS = True
