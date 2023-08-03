# Splatoon3-Randomizer
A randomizer for Splatoon 3 Hero Mode. Currently still very early in development.

This release version allows for shuffling levels, weapons, ink color, and music. Grizzco weapons are included, as well as being able to use the Rainmaker! There is also the option to add a "Enemy ink is lava" challenge to every level

Please note that while most things are functional, this randomizer is still very early in development and lacks proper logic. There is a definite possibilty in levels being unbeatable. There is a setting that at least tries to prevent this

In order to run the randomizer, you must have the RomFS of the game extracted and on the device you're running this program from. This can be extracted through tools like [Hactool](https://github.com/SciresM/hactool) or [nxdumptool] from the Homebrew App Store. The RomFS is the component of the game package with all of the data files (i.e. non-executable files). Currently, only the `Pack/Scene` folder is required.

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

To play the randomizer, you will either need a homebrewed Switch console or a Nintendo Switch emulator.

The randomizer does not provide a second copy of the game to use, but rather makes use of the LayeredFS system for applying game mods. The simple way to explain this system is that we will provide a secondary RomFS which is external to the game's internal RomFS, and will force the game to use any corresponding external file instead of the internal one, provided an external one exists. This functionality is simple to set up.

(See also: [Switch game modding](https://nh-server.github.io/switch-guide/extras/game_modding/))

Switch: On your SD card for your homebrew setup, navigate to the `Atmosphere/contents` folder and create a new directory named `0100C2500FC20000`. Copy and paste the `Romfs` folder from the randomizer output into this new folder. That is, the folder structure here should look like `Atmosphere/contents/0100C2500FC20000/Romfs/...`. After this, relaunch CFW and simply start up Link's Awakening to play the randomizer!

Emulator: Open up the mods folder and create a new directory named `0100C2500FC20000`. Enter it and create a new folder named whatever you want. Inside that should be the `Romfs` folder from the randomizer output. It should look something like `%ModsDir%/0100C2500FC20000/LASRando/Romfs/...`

Applying this mod will not in any way affect your save data, so don't delete anything you don't want deleted. If you want to go back to the original game after, either manually clear the files out, or you can launch the game holding L
