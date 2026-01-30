# I might want to edit and add new colors, which is why this is in its own script

from randomizer_paths import DATA_PATH

with open(DATA_PATH / "HeroMode" / "colors.txt", "r") as f:
    COLORS = f.read().splitlines()


def getRandomColor(rng) -> str:
    return rng.choice(COLORS)
