from PySide6.QtCore import QObject
from RandomizerCore.Randomizers.HeroMode import HeroMode_Process
from RandomizerCore.Randomizers.SideOrder import SideOrder_Process
from RandomizerCore.Tools.zs_tools import BYAML, SARC
from pathlib import Path


class RandomizersCore(QObject):
    """A container for managing the threads for the different randomizers

    This also holds shared functions for loading and saving files"""

    def __init__(self, window, settings: dict) -> None:
        super().__init__(window)
        self.window = window
        self.rom_path = Path(settings["RomFS"])
        self.out_dir = Path(settings["Output"])
        self.seed = str(settings["Seed"])
        self.hm_settings = dict(settings["HeroMode"])
        self.so_settings = dict(settings["SideOrder"])
        self.version = self.getGameVersion()


    def randomizeHeroMode(self) -> bool:
        """Starts the HeroMode_Process thread

        The thread is linked to the progress window"""

        if not any(v for k,v in self.hm_settings.items()):
            return False

        self.current_process = HeroMode_Process(self, self.seed, self.hm_settings)
        self.current_process.status_update.connect(self.window.updateStatus)
        self.current_process.error.connect(self.window.modsError)
        self.current_process.is_done.connect(self.window.modsDone)
        self.current_process.start()
        return True


    def randomizeSideOrder(self) -> bool:
        """Starts the SideOrder_Process thread

        The thread is linked to the progress window"""

        if not any(v for k,v in self.so_settings.items()):
            return False

        self.current_process = SideOrder_Process(self, self.seed, self.so_settings)
        self.current_process.status_update.connect(self.window.updateStatus)
        self.current_process.error.connect(self.window.modsError)
        self.current_process.is_done.connect(self.window.modsDone)
        self.current_process.start()
        return True


    def stop(self) -> None:
        """Tells the current thread to cancel"""

        self.current_process.thread_active = False


    def getGameVersion(self) -> str:
        """Get the version string from the RSDB folder in the RomFS

        Uses the highest version if multiple exists"""

        rsdb_path = self.rom_path / "RSDB"
        markers = [int(f.stem.split('.')[2], 16) for f in rsdb_path.iterdir()
                   if f.stem.startswith("ActorInfo")]
        version_string = hex(max(markers))[2:].lower()
        return version_string


    def loadFile(self, relative_path: str, base_name: str) -> tuple[str, BYAML | SARC]:
        """Loads a file within the RomFS

        Uses the file already in the output if one exists"""

        if '.' in base_name:
            file_name = base_name
        else:
            file_name = [f.name for f in (self.rom_path / relative_path).iterdir()
                        if f.name.startswith(base_name)
                        and f.name.split('.')[2] == self.version][0]

        file_path = self.out_dir / relative_path / file_name
        if not file_path.exists():
            file_path = self.rom_path / relative_path / file_name

        if file_name.endswith(".byml.zs"):
            with open(file_path, "rb") as f:
                data = BYAML(f.read(), compressed=True)
        else:
            with open(file_path, "rb") as f:
                data = SARC(f.read())

        return file_name, data


    def saveFile(self, relative_path: str, file_name: str, data) -> None:
        """Saves a file to the output directory"""

        with open(self.out_dir / relative_path / file_name, "wb") as f:
            f.write(data.repack())


    def loadFromSarc(self, sarc: SARC, file_path: str) -> BYAML:
        """Loads a file from a SARC archive

        Currently only loads BYAMLs"""

        match file_path.split('.')[-1]:
            case "byml" | "bgyml":
                byaml = BYAML(sarc.writer.files[file_path])
                return byaml
            case _:
                raise TypeError("core.loadFromSarc: Could not determine file type!")


    def saveToSarc(self, sarc: SARC, file_path: str, data) -> None:
        """Saves a file to a SARC archive"""

        sarc.writer.files[file_path] = data.repack()
