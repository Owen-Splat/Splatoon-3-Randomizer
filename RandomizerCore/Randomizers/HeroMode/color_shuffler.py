# I might want to edit and add new colors, which is why this is in its own script

from randomizer_paths import DATA_PATH
import oead

with open(DATA_PATH / "HeroMode" / "colors.txt", "r") as f:
    COLORS = f.read().splitlines()


def getRandomColor(rng) -> str:
    """Gets a random color from the list"""

    return rng.choice(COLORS)


def editColors(thread) -> None:
    """Edits the RGB values of each entry in the color list"""

    file_name, color_data = thread.parent().loadFile("RSDB", "TeamColorDataSet")

    for color_types in color_data.info:
        if "AlphaTeamColor" in color_types:
            color_types["AlphaTeamColor"]["B"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["AlphaTeamColor"]["G"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["AlphaTeamColor"]["R"] = oead.F32(thread.rng.uniform(0, 1))
        if "BravoTeamColor" in color_types:
            color_types["BravoTeamColor"]["B"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["BravoTeamColor"]["G"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["BravoTeamColor"]["R"] = oead.F32(thread.rng.uniform(0, 1))
        if "CharlieTeamColor" in color_types:
            color_types["CharlieTeamColor"]["B"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["CharlieTeamColor"]["G"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["CharlieTeamColor"]["R"] = oead.F32(thread.rng.uniform(0, 1))
        if "NeutralColor" in color_types:
            color_types["NeutralColor"]["B"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["NeutralColor"]["G"] = oead.F32(thread.rng.uniform(0, 1))
            color_types["NeutralColor"]["R"] = oead.F32(thread.rng.uniform(0, 1))

    thread.parent().saveFile("RSDB", file_name, color_data)
