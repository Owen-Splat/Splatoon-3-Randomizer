from version import VERSION
from pathlib import Path
import platform, shutil, sys

base_name = 'Splatoon 3 Randomizer'

exe_ext = ""
if platform.system() == "Windows":
    exe_ext = ".exe"
    platform_name = "win"
if platform.system() == "Darwin":
    exe_ext = ".app"
    platform_name = "mac"
if platform.system() == "Linux":
    platform_name = "linux"

exe_path = Path(sys.argv[0]).parent.absolute() / 'dist' / str(base_name + exe_ext)
if not (exe_path.is_file() or exe_path.is_dir()):
    raise Exception("Executable not found: %s" % exe_path)

release_path = Path(".") / "dist" / str("release_archive_" + VERSION)
print("Writing build to path: %s" % (release_path))

if release_path.exists() and release_path.is_dir():
    shutil.rmtree(release_path)

release_path.mkdir(parents=True, exist_ok=True)
shutil.copyfile("README.md", release_path / "README.txt")

shutil.move(exe_path, release_path / str(base_name + exe_ext))
