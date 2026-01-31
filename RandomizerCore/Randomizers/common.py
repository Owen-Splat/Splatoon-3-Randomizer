from RandomizerCore.Tools.zs_tools import BYAML, SARC
from pathlib import Path


# TODO: We will need this for randomizing Side Order as well to check valid weapons
# There will probably be other general functions we will need as well
# e.g. Streamlined Read/Write functions with automatic error handling
# These functions/scripts will be in the root RandomizerCore/Randomizers folder
def getGameVersion(rom_path: Path) -> str:
    """Get the version string from the RSDB folder in the RomFS

    In the case of the user having dumped multiple updates into the same directory, get the highest one"""

    rsdb_path = rom_path / "RSDB"
    markers = [int(f.stem.split('.')[2], 16) for f in rsdb_path.iterdir() if f.stem.startswith("ActorInfo")]
    version_string = hex(max(markers))[2:].lower()
    return version_string


def loadRSDB(rom_path: Path, base_name: str) -> tuple[str, BYAML]:
    """Parses a BYAML file from RomFS/RSDB"""

    file_name = [f.name for f in (rom_path / 'RSDB').iterdir()
                    if f.name.startswith(base_name)
                    and f.name.split('.')[2] == getGameVersion(rom_path)][0]

    with open(rom_path / 'RSDB' / file_name, 'rb') as f:
        rsdb = BYAML(f.read(), compressed=True)

    return file_name, rsdb


def saveRSDB(out_path: Path, name: str, rsdb: BYAML) -> None:
    with open(out_path / 'RSDB' / name, 'wb') as f:
        f.write(rsdb.repack())


def loadScene(rom_path: Path, name: str) -> SARC:
    """Parses a SARC file from RomFS/Pack/Scene"""

    with open(rom_path / 'Pack' / 'Scene' / name, 'rb') as f:
        sarc = SARC(f.read())

    return sarc


def loadFromSarc(sarc: SARC, file_path: str) -> BYAML:
    match file_path.split('.')[-1]:
        case "byml" | "bgyml":
            byaml = BYAML(sarc.writer.files[file_path])
            return byaml
        case _:
            raise TypeError("common.loadFromSarc: Could not determine file type!")


def saveToSarc(sarc: SARC, file_path: str, file_data: bytes) -> None:
    sarc.writer.files[file_path] = file_data


def loadSarc(file_path: Path) -> SARC:
    with open(file_path, 'rb') as f:
        sarc = SARC(f.read())
    return sarc


def loadSingletonParams(rom_path: Path) -> tuple[str, SARC]:
    singleton_files = [f.name for f in (rom_path / 'Pack').iterdir()
                       if f.name.startswith('SingletonParam')]
    if not singleton_files:
        return

    for f in singleton_files: # if there is a SingletonParam_v700 or higher, use that
        param_file = f

    param_sarc = loadSarc(rom_path / "Pack" / param_file)
    return param_file, param_sarc


def saveSingletonParams(out_path: Path, file_name: str, param_sarc: SARC) -> None:
    with open(out_path / 'Pack' / file_name, 'wb') as f:
        f.write(param_sarc.repack())
