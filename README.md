# Splatoon-3-Randomizer
A randomizer for Splatoon 3 Hero Mode

You can download the randomizer here: https://github.com/Owen-Splat/Splatoon-3-Randomizer/releases/latest

**NOTE**: This mod is not online safe. To avoid getting your Nintendo Switch banned, you should always play mods on emuMMC. Playing offline is not enough as some games (like Splatoon 3) stores telemetry that will then be sent to Nintendo the next time the console is connected to the internet

## Information
This randomizer allows for shuffling levels, weapons, ink color, music, enemies, and much more! There is logic in place to ensure that every seed should be able to be finished, however it is a work in progress and as such there may be occasional issues. Please report them either on this repository or notify me on Discord or Bluesky *@Owen_Splat*

In order to run the randomizer, you must have the RomFS of the game extracted and on the device you're running this program from. This can be extracted on pc using your emulator of choice, or on console using nxdumptool from the Homebrew App Store. The RomFS is the component of the game package with all of the data files (i.e. non-executable files). You **NEED** to make sure that the RomFS dump includes the update RomFS that you are playing on, otherwise key features of the randomizer will not work correctly

Please make sure that your RomFS dump matches the version that you will be playing on! Version mismatches will cause issues!

## Running from source:
**NOTE**: This is for advanced users or those helping with the development of the randomizer.

If you want to run from source, then you need to clone this repository and make sure you have Python 3.12.8 installed. Due to the dependencies, earlier and later versions will not work

Open the folder in a command prompt and install dependencies by running:  
`py -3.12 -m pip install -r requirements.txt` (on Windows)  
`python3 -m pip install -r requirements.txt` (on Mac)  
`python3 -m pip install $(cat requirements.txt) --user` (on Linux)

Then run the randomizer with:  
`py -3.12 randomizer.py` (on Windows)  
`python3 randomizer.py` (on Mac)  
`python3 randomizer.py` (on Linux)  

If you wish to build this into an executable yourself, run the included **build.bat** file

## How to play:
To play the randomizer, you will either need a homebrewed Switch console or a Nintendo Switch emulator

The randomizer does not provide a second copy of the game to use, but rather makes use of the LayeredFS system for applying game mods. The simple way to explain this system is that it will force the game to use external files instead of the internal ones. This functionality is simple to set up

(See also: [Switch game modding](https://nh-server.github.io/switch-guide/extras/game_modding/))

Switch: Set the platform to Console and generate the seed. Simply drag the `atmosphere` folder to the root of your SD card. The folder structure here should look like `atmosphere/contents/0100C2500FC20000/romfs/...`. After this, simply start up Splatoon 3 while in CFW

Emulator: Set the output folder to your Splatoon 3 mods directory. You can right click the game in the emulator to find it. Set the platform to Emulator and generate the seed. Then just start up the game with the mod enabled

Enjoy the randomizer!