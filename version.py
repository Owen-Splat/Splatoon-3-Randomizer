from randomizer_paths import ROOT_PATH

with open(ROOT_PATH / "version.txt", "r") as f:
    VERSION = f.read().strip()