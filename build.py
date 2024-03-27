import os
import sys
import shutil
from RandomizerCore.Data.randomizer_data import VERSION

import struct
if (struct.calcsize("P") * 8) == 64:
	bitness_suffix = "_x64"
else:
	bitness_suffix = "_x32"

base_name = f"S3Rando-{VERSION}-{sys.platform}{bitness_suffix}"
build_path = os.path.join(".", "build")
freeze_path = os.path.join(build_path, "exe.win-amd64-3.8")
release_path = os.path.join(build_path, base_name)

if os.path.exists(release_path) and os.path.isdir(release_path):
  shutil.rmtree(release_path)

os.rename(freeze_path, release_path)
shutil.copyfile("README.md", os.path.join(release_path, "README.txt"))
shutil.copyfile("LICENSE.txt", os.path.join(release_path, "LICENSE.txt"))
shutil.move(os.path.join(release_path, "RandomizerCore/Data"), os.path.join(release_path, "Data"))
shutil.move(os.path.join(release_path, "RandomizerUI/Resources"), os.path.join(release_path, "Resources"))
shutil.make_archive(release_path, "zip", release_path)
