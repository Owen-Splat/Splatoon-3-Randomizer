import sys
from cx_Freeze import setup, Executable
from randomizer_data import VERSION

build_exe_options = {"packages": ["os"], 
                    "excludes": ["tkinter", "unittest", "sqlite3", "numpy", "matplotlib", "keystone-engine"],
                    "zip_include_packages": ["encodings", "PySide6"],
                    "include_files": ["Data", "Resources"],
                    "optimize": 2}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_icon = "Resources/icon.ico"
if sys.platform == "darwin": # mac
    build_icon = "Resources/icon.icns"

setup(
    name = "Splatoon 3 Randomizer",
    version = f"{VERSION}",
    description = "A randomizer for Splatoon 3 Hero Mode",
    options = {"build_exe": build_exe_options},
    executables = [Executable("randomizer.py", base=base, target_name="Splatoon 3 Randomizer", icon=build_icon)]
)