from randomizer_paths import *

import yaml
import os

VERSION = "0.2.0"

with open(os.path.join(DATA_PATH, 'seeds.yml'), 'r') as f:
    seed_info = yaml.safe_load(f)
    ADJECTIVES = seed_info['Adjectives']
    CHARACTERS = seed_info['Characters']

with open(os.path.join(DATA_PATH, 'parameters.yml'), 'r') as f:
    PARAMS = yaml.safe_load(f)

try:
    with open(SETTINGS_PATH, 'r') as f:
        SETTINGS = yaml.safe_load(f)
        DEFAULTS = False
except FileNotFoundError:
    DEFAULTS = True
