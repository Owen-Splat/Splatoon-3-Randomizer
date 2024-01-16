# Splatoon-3-Randomizer
A randomizer for Splatoon 3 Hero Mode. Currently still very early in development

This release version allows for shuffling levels, weapons, ink color, and music. Grizzco weapons are included, as well as being able to use the Rainmaker! There is also the option to add a "Enemy ink is lava" challenge to every level

Please note that while most things are functional, this randomizer is still very early in development and lacks proper logic. There is a definite possibilty in levels being unbeatable. There is a setting that at least tries to prevent this by keeping the first weapon as vanilla

In order to run the randomizer, you must have the RomFS of the game extracted and on the device you're running this program from. This can be extracted on pc through Yuzu or Ryujinx, or nxdumptool from the Homebrew App Store. The RomFS is the component of the game package with all of the data files (i.e. non-executable files)

The season that you choose to play should match the major version number that you are playing on. For example, if you are playing on version 5.1.0, you should select season 5. If you choose a season higher than your game version, the randomizer will shuffle in weapons that aren't supported by your version, which results in having no weapon in that slot

## How to run:

Either just download the latest release, which will automatically be updated to include the latest build, or you can also run from source.
If you want to run from source, then you need to clone this repository and make sure you have Python 3.8+ installed

Open the folder in a command prompt and install dependencies by running:  
`py -3.8 -m pip install -r requirements.txt` (on Windows)  
`python3 -m pip install -r requirements.txt` (on Mac)  
`python3 -m pip install $(cat requirements.txt) --user` (on Linux)

Then run the randomizer with:  
`py -3.8 randomizer.py` (on Windows)  
`python3 randomizer.py` (on Mac)  
`python3 randomizer.py` (on Linux)  

If you are using a higher version of Python, change the commands to include your version instead

## How to build:

Once you have installed all the requirements, there is an included **build.bat** file. Run that and it will automatically enter the commands to create a build. Once again, if you are using a higher version of Python, you will need to edit this file to match your version

## How to play:

To play the randomizer, you will either need a homebrewed Switch console or a Nintendo Switch emulator

The randomizer does not provide a second copy of the game to use, but rather makes use of the LayeredFS system for applying game mods. The simple way to explain this system is that we will provide a secondary RomFS which is external to the game's internal RomFS, and will force the game to use any corresponding external file instead of the internal one, provided an external one exists. This functionality is simple to set up

(See also: [Switch game modding](https://nh-server.github.io/switch-guide/extras/game_modding/))

Switch: Set the platform to Console and generate the seed. Simply drag the `atmosphere` folder to the root of your SD card. The folder structure here should look like `atmosphere/contents/0100C2500FC20000/romfs/...`. After this, simply start up Splatoon 3 while in CFW and enjoy the randomizer!

Emulator: Set the platform to Emulator and generate the seed. Simply drag the seed folder into the Splatoon 3 mods directory. You can right click the game in the emulator to find it. Then just start up the game with the mod enabled and enjoy the randomizer!

Applying this mod will not in any way affect your save data, so don't delete anything you don't want deleted. If you want to go back to the original game after, either manually clear the files out, or you can launch the game holding L
