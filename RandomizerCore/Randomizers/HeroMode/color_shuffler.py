# I might want to edit and add new colors, which is why this is in its own script

from randomizer_paths import DATA_PATH
import oead

with open(DATA_PATH / "HeroMode" / "colors.txt", "r") as f:
    COLORS = f.read().splitlines()


class Color:
    """Represents a traditional rgb color with oead byml compatible packing"""

    def __init__(self, r: int, g: int, b: int) -> None:
        self.r = r
        self.g = g
        self.b = b


    def pack(self) -> dict:
        """Converts the 0-255 values to a 0-1 oead.F32 range"""

        return {
            "R": oead.F32(self.r / 255),
            "G": oead.F32(self.g / 255),
            "B": oead.F32(self.b / 255),
            "A": oead.F32(1.0)
        }


    def inversePack(self) -> None:
        """Converts the inverted 0-255 values to a 0-1 oead.F32 range"""

        return {
            "R": oead.F32((255 - self.r) / 255),
            "G": oead.F32((255 - self.g) / 255),
            "B": oead.F32((255 - self.b) / 255),
            "A": oead.F32(1.0)
        }


def getRandomColor(rng) -> str:
    """Gets a random color from the list"""

    return rng.choice(COLORS)


def editColors(thread) -> None:
    """Edits the RGB values of each entry in the color list"""

    file_name, color_data = thread.parent().loadFile("RSDB", "TeamColorDataSet")

    for color_type in color_data.info:
        if not thread.thread_active:
            break

        name = color_type["__RowId"].split('/')[2].split('.')[0]
        if name not in COLORS:
            # we exclude boss color sets from the pool, but we still want to change the colors
            if not name.startswith("HeroBoss"):
                continue

        # get the boss ink color, otherwise use the generic enemy ink color
        if "Boss" in name:
            bravo_raw = color_type["BravoTeamColor"]
            r,g,b = (float(bravo_raw["R"]), float(bravo_raw["G"]), float(bravo_raw["B"]))
            bravo = Color(int(r * 255), int(g * 255), int(b * 255))
        else:
            bravo = Color(200, 30, 180)

        # make sure the player ink color is not too similar to the enemy ink
        alpha = createRandomColor(thread.rng)
        while checkColorSimilarity(bravo, alpha):
            alpha = createRandomColor(thread.rng)

        # change player color
        color_type["AlphaTeamColor"] = alpha.pack()

        # change boss colors (the ink they paint stays the same, not yet sure how to change it)
        color_type["BravoTeamColor"] = alpha.inversePack()

    thread.parent().saveFile("RSDB", file_name, color_data)


def createRandomColor(rng) -> Color:
    """Creates a random color"""

    return Color(rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))


def checkColorSimilarity(color1: Color, color2: Color) -> bool:
    """Checks whether two colors are similar or not"""

    diff = abs(color1.r - color2.r) + abs(color1.g - color2.g) + abs(color1.b - color2.b)
    return diff < 165
