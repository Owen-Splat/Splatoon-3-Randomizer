from RandomizerCore.Tools.zs_tools import BYAML
from randomizer_paths import DATA_PATH
import oead, time, yaml

with open(DATA_PATH / "weapons.yml", "r") as f:
    WEAPONS = yaml.safe_load(f)

with open(DATA_PATH / "HeroMode" / "logic.yml", "r") as f:
    LOGIC = yaml.safe_load(f)


def getValidMainWeapons(thread) -> list[str]:
    version_string = thread.parent().version

    # Now get the season corresponding to the version. This is just the major version marker besides 1.0.0 which is season 0
    match version_string:
        case "100":
            season = 0
        case _: # default
            season = int(version_string[0], 16)

    # Now use the season to get all the valid weapons listed in our PARAMS file
    valid_seasons = [k for k in WEAPONS['Main_Weapons'] if int(k.split('_')[-1]) <= season]
    main_weapons_list = []
    for season in valid_seasons:
        for weapon in WEAPONS['Main_Weapons'][season]:
            main_weapons_list.append(weapon)

    return main_weapons_list


def randomizeWeapons(thread, hero_weapons: list[str]) -> dict:
    """Creates a dict of levels and weapon choices. Each level is given 3 choices"""

    # Update the ui status and add a slight delay so that the user has time to read it
    thread.status_update.emit("Randomizing weapons...")
    time.sleep(1)

    weapon_placements = {}

    main_weapons_list = getValidMainWeapons(thread)
    for wep in hero_weapons:
        main_weapons_list.remove(wep)

    # Now for each level in the logic file, randomly assign 3 weapon choices in increasing difficulty
    # If any are not valid for the given level, reroll
    for k,v in LOGIC["Missions"].items():
        if not thread.thread_active:
            break
        if "Special" in v: # ignore zipcaster & inkjet levels for now
            continue
        weapons = []
        for i in range(3):
            if not thread.thread_active:
                break
            if (not str(k).endswith('C')) and (i == 0): # keep hero weapon choice since the hero weapon is randomized
                weapons.append("Hero")
                continue
            w = assignWeapon(thread, main_weapons_list, i)
            while not checkIfWeaponIsValid(w, v):
                w = assignWeapon(thread, main_weapons_list, i)
            weapons.append(w)
        weapon_placements[f"Msn_{k}"] = weapons

    return weapon_placements

# TODO: MAKE SURE THE USER DOES NOT GET REPEAT WEAPON CHOICES
def assignWeapon(thread, main_weapons: list, index: int) -> str:
    """Assigns a random weapon of difficulty index with no regard of the level logic"""

    # Since we are using index as the difficulty, add one so we dont multiply by 0
    # This gives us a difficulty rating of 1-3
    difficulty = index + 1

    # Add a chance for special with the chance decreasing based on the difficulty value
    # Since we reroll if the weapon is not valid, there will be more rolls so odds are technically higher
    # 1/8 -> 1/12 -> 1/16
    odds = 8
    odds += 4 * (difficulty - 1)
    special = ""
    if thread.rng.random() < (1 / odds):
        special = thread.rng.choice(WEAPONS["Special_Weapons"])
        if special != "SpSuperHook_Mission":
            return special

    # Determine the weight of each class in regards to the difficulty value
    # This will be reformatted into something more readable, but this is fine for testing what weapons are typically easier or harder 
    class_weights = {
        "Shooter": 4 - difficulty,
        "Blaster": 3 / difficulty,
        "Roller": 3 / difficulty,
        "Brush": 3 / difficulty,
        "Charger": 4 - difficulty,
        "Slosher": 3 / difficulty,
        "Spinner": 4 - difficulty,
        "Maneuver": 4 - difficulty,
        "Shelter": 0.5 + (difficulty - 1),
        "Stringer": 4 - difficulty,
        "Saber": 0.5 + (difficulty - 1),
        "Free": 0 + ((difficulty - 1) * 2)
    }

    # Now make a dict of the weapon names with the class difficulty
    mains_with_weights = {}
    for m in main_weapons:
        if not thread.thread_active:
            break
        for k,v in class_weights.items():
            if not thread.thread_active:
                break
            if m.startswith(k):
                mains_with_weights[m] = v
                break

    # Now get a random main weapon using the weights
    main = thread.rng.choices(list(mains_with_weights.keys()), list(mains_with_weights.values()))[0]
    if special:
        result = f"{special}+{main}"
        return result

    # Now we do the same for sub weapons
    # Besides just difficulty, we need to ensure that we attempt to give a proper bomb if the main weapon is empty
    has_main = True if main == "Free" else False
    sub_weights = {
        "Beacon": difficulty * has_main,
        "Bomb_Curling_Mission": 4 - difficulty,
        "Bomb_Fizzy": 3 / difficulty,
        "Bomb_Quick_Mission": 4 - difficulty,
        "Bomb_Robot_Mission": 4 - difficulty,
        "Bomb_Splash_Mission": 4 - difficulty,
        "Bomb_Suction_Mission": 4 - difficulty,
        "Bomb_Torpedo": 3 / difficulty,
        "LineMarker": 0.5 + (difficulty - 1),
        "PointSensor": difficulty * has_main,
        "PoisonMist": difficulty * has_main,
        "SalmonBuddy": 3 / difficulty,
        "Shield": difficulty * has_main,
        "Sprinkler": difficulty * has_main,
        "Trap_Mission": 3 / difficulty,
        "Free": difficulty * has_main
    }
    sub = thread.rng.choices(list(sub_weights.keys()), list(sub_weights.values()))[0]

    result = f"{main}+{sub}"
    return result


def checkIfWeaponIsValid(weapon: str, level_logic: dict) -> bool:
    """Checks if the randomly assigned weapon is valid against the level logic"""

    result = True

    # 2 unique cases where the level is designed around curling bomb/linemarker
    if "Sub" in level_logic:
        if not weapon.endswith(level_logic["Sub"]):
            result = False

    # Special
    if weapon.startswith("Sp") and not weapon.startswith("Spinner"):
        special = weapon.split('+')[0]
        weapon_logic = LOGIC["Special_Weapons"][special]
        if weapon_logic["Range"] < level_logic["Range"]:
            result = False
        if (not weapon_logic["Floor_Paint"]) and (level_logic["Floor_Paint"]):
            result = False
        if (not weapon_logic["Wall_Paint"]) and (level_logic["Wall_Paint"]):
            result = False
        if (not weapon_logic["Rail"]) and (level_logic["Rail"]):
            result = False
        if (not weapon_logic["Grate"]) and (level_logic["Grate"]):
            result = False
        return result

    # Main + Sub
    if '+' in weapon:
        main, sub = weapon.split('+')
        main_parts = main.split('_')
        main_without_last = main_parts[:-1]
        main = "_".join(main_without_last)
        main_logic = LOGIC["Main_Weapons"][main]
        sub_logic = LOGIC["Sub_Weapons"][sub]
        if "Main" in level_logic: # only a couple levels include this param and its always true
            if main == "Free":
                result = False
        if main_logic["Range"] < level_logic["Range"]:
            if sub_logic["Range"] < level_logic["Range"]:
                result = False
            if (not sub_logic["Floor_Paint"]) and (level_logic["Floor_Paint"]):
                result = False
            if (not sub_logic["Wall_Paint"]) and (level_logic["Wall_Paint"]):
                result = False
            if level_logic["Attack"]:
                if not sub_logic["Attack"]:
                    result = False
        return result

    # Main only
    weapon_parts = weapon.split('_')
    weapon_without_last = weapon_parts[:-1]
    weapon = "_".join(weapon_without_last)
    main_logic = LOGIC["Main_Weapons"][weapon]
    if main_logic["Range"] < level_logic["Range"]: # this covers no weapon
        result = False

    return result


# TODO: Add zipcaster to levels that need it
# We will eventually add objects to zipcaster/inkjet levels so any weapon can beat it
# Right now, any weapon is valid in zipcaster levels since the zipcaster beats them by itself
# Once we edit these special levels, we will need to add proper logic
def editWeaponChoices(thread, mission_name: str, mission_data: BYAML) -> None:
    """Edits the weapon choices in the mission data to the new randomized weapons

    The mission weapon data is then copied over to the ui mission data.
    This makes the weapon choices visible when standing over kettles"""

    if mission_name.split('_', 1)[1] not in LOGIC["Missions"]:
        return

    # skip over editing data for levels that we keep vanilla (zipcaster and inkjet levels)
    if mission_name in thread.weapon_placements:
        if len(mission_data.info['OctaSupplyWeaponInfoArray']) > 0:
            while len(mission_data.info['OctaSupplyWeaponInfoArray']) < 3:
                mission_data.info['OctaSupplyWeaponInfoArray'].append(
                    mission_data.info['OctaSupplyWeaponInfoArray'][-1])

        for i in range(len(mission_data.info['OctaSupplyWeaponInfoArray'])):
            e = mission_data.info['OctaSupplyWeaponInfoArray'][i]

            if i == 0: # leave first option as vanilla if it is a hero weapon
                try:
                    if e['SupplyWeaponType'] == 'Hero':
                        continue
                except KeyError:
                    pass

            weapon = thread.weapon_placements[mission_name][i]

            if weapon.startswith("Sp") and not weapon.startswith("Spinner"):
                if '+' in weapon:
                    special_weapon, main_weapon = weapon.split('+')
                else:
                    special_weapon = weapon
                    main_weapon = "Free"
                e['SubWeapon'] = ""
                e['SpecialWeapon'] = f"Work/Gyml/{special_weapon}.spl__WeaponInfoSpecial.gyml"
                if weapon.startswith("SpSuperHook_Mission"):
                    e["SupplyWeaponType"] = "MainAndSpecial"
                    e['WeaponMain'] = f"Work/Gyml/{main_weapon}.spl__WeaponInfoMain.gyml"
                    if main_weapon == "Free":
                        e["WeaponMain"] = ""
                else:
                    e["SupplyWeaponType"] = "Special"
                continue

            e['SupplyWeaponType'] = "Normal"
            main_weapon, sub_weapon = weapon.split('+')
            e['WeaponMain'] = f"Work/Gyml/{main_weapon}.spl__WeaponInfoMain.gyml"
            e['SubWeapon'] = f"Work/Gyml/{sub_weapon}.spl__WeaponInfoSub.gyml"
            if main_weapon == "Free":
                e["WeaponMain"] = ""
            if sub_weapon == "Free":
                e["SubWeapon"] = ""

    thread.ui_missions_info[mission_name] = mission_data.info['OctaSupplyWeaponInfoArray']


def randomizeHeroWeapons(thread) -> list[str]:
    """Pulls 3 unique weapons to replace the hero shot and upgrades"""

    return thread.rng.sample(getValidMainWeapons(thread), 3)


def replaceHeroWeaponEntries(core, hero_weps: list[str]) -> None:
    """Deletes the hero weapon entries and assigns their IDs to each entry in hero_weps"""

    file_name, weapons_info = core.loadFile("RSDB", "WeaponInfoMain")

    hero_ids = [oead.S32(10900), oead.S32(10910), oead.S32(10920)]

    for entry in list(weapons_info.info):
        if entry["Id"] in hero_ids:
            weapons_info.info.remove(entry)

    i = 0
    for entry in weapons_info.info:
        if i > 2:
            break
        if entry["__RowId"] in hero_weps:
            entry["Id"] = hero_ids[hero_weps.index(entry["__RowId"])]
            i += 1

    core.saveFile("RSDB", file_name, weapons_info)


def editLevelWeaponUI(thread) -> None:
    """Edits the mission info in MissionMapInfo to match the mission info inside the level SARC

    This controls what displays when standing over the kettles"""

    info_name, ui_info_file = thread.parent().loadFile("RSDB", "MissionMapInfo")

    for msn_info in ui_info_file.info:
        msn_name = msn_info["__RowId"]
        if msn_name in thread.ui_missions_info:
            msn_info['OctaSupplyWeaponInfoArray'] = thread.ui_missions_info[msn_name]

    thread.ui_missions_info.clear()
    thread.parent().saveFile("RSDB", info_name, ui_info_file)
