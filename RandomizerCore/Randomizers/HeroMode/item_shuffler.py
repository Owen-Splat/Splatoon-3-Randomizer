from RandomizerCore.Tools.zs_tools import BYAML, SARC
import oead

DROPS = {
    "ItemArmor": 2,
    "ItemCanSpecial_Blower": 1,
    "ItemCanSpecial_Chariot": 1,
    "ItemCanSpecial_InkStorm": 1,
    "ItemCanSpecial_Jetpack": 1,
    "ItemCanSpecial_MicroLaser": 1,
    "ItemCanSpecial_MultiMissile": 1,
    "ItemCanSpecial_ShockSonar": 1,
    "ItemCanSpecial_Skewer": 1,
    "ItemCanSpecial_SuperHook": 1,
    "ItemCanSpecial_SuperLanding": 1,
    "ItemCanSpecial_TripleTornado": 1,
    "ItemCanSpecial_UltraShot": 1,
    "ItemCanSpecial_UltraStamp": 1,
    "ItemIkura": 2,
    "ItemIkuraBottle": 5,
    "ItemIkuraLarge": 3,
    "ItemInkBottle": 2,
    "EnemyBombTakopter": 2,
    "EnemyBoostTakopter": 2,
    "EnemyTakopter": 2,
    "EnemyTakodozer": 2,
    "EnemyTakoHopper": 2,
    "EnemyTakolienVehicle": 2
}


def randomizeItems(thread, level_sarc: SARC) -> None:
    """Iterates through the actors to find item drops and changes what drops"""

    # read banc file which contains the actor list
    file_path = [f.name for f in list(level_sarc.reader.get_files())
                 if f.name.startswith("Banc/")][0]
    banc: BYAML = thread.parent().loadFromSarc(level_sarc, file_path)

    # get all the linked items to be dropped
    linked_ids = []
    for act in banc.info["Actors"]:
        if "Links" in act:
            for link in act["Links"]:
                if link["Name"] == "ToDropItem":
                    linked_ids.append(link["Dst"])

    # iterate through them and change the object type
    # keys need to be left vanilla
    for act in banc.info["Actors"]:
        if act["Hash"] not in linked_ids:
            continue
        if act["Name"] == "ItemCardKey":
            continue
        new_item = thread.rng.choices(list(DROPS.keys()), list(DROPS.values()))[0]
        act['Gyaml'] = new_item
        act['Name'] = new_item
        if new_item == 'ItemIkuraBottle':
            act['spl__ItemIkuraBottleBancParam'] = {
                'DropIkuraValue': oead.S32(10),
                'DropNum': oead.S32(10)
            }

    # we could go through the boxes that just gives power eggs and make new drops
    # but that can wait, lets see how it currently feels

    # save banc file
    thread.parent().saveToSarc(level_sarc, file_path, banc)