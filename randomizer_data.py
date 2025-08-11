from randomizer_paths import *
import yaml

with open(RESOURCE_PATH / 'adjectives.txt', 'r') as f:
    ADJECTIVES = f.read().splitlines()

with open(RESOURCE_PATH / 'characters.txt', 'r') as f:
    CHARACTERS = f.read().splitlines()

with open(RESOURCE_PATH / 'changelog.txt', 'r') as f:
    CHANGES = f.read()

with open(DATA_PATH / 'parameters.yml', 'r') as f:
    PARAMS = yaml.safe_load(f)

try:
    with open(SETTINGS_PATH, 'r') as f:
        SETTINGS = yaml.safe_load(f)
        DEFAULTS = False
except FileNotFoundError:
    DEFAULTS = True
