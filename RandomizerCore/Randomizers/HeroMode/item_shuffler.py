from RandomizerCore.Tools.zs_tools import BYAML, SARC
from RandomizerCore.Tools.actor_tools import SplActor
import oead

# we only include one enemy entry because it gets removed if enemies arent randomized
# enemies get randomized after the item drops, so it will turn into a different enemy anyway
DROPS = {
    "ItemArmor": 1.5,
    "ItemCanSpecial_Blower": 0.2,
    "ItemCanSpecial_Chariot": 0.2,
    "ItemCanSpecial_InkStorm": 0.2,
    "ItemCanSpecial_Jetpack": 0.2,
    "ItemCanSpecial_MicroLaser": 0.2,
    "ItemCanSpecial_MultiMissile": 0.2,
    "ItemCanSpecial_ShockSonar": 0.2,
    "ItemCanSpecial_Skewer": 0.2,
    "ItemCanSpecial_SuperHook": 0.2,
    "ItemCanSpecial_SuperLanding": 0.2,
    "ItemCanSpecial_TripleTornado": 0.2,
    "ItemCanSpecial_UltraShot": 0.2,
    "ItemCanSpecial_UltraStamp": 0.2,
    # "ItemIkura": 2.5, # no physics so it floats where it spawns. works fine but looks weird
    "ItemIkuraBottle": 5.0,
    # "ItemIkuraLarge": 4.0, # grizz power eggs?
    "ItemInkBottle": 2.0,
    "EnemyTakopter": 4.0
}

VANILLA_DROPS = (
    "ItemCardKey",
    "ItemCanInfinitySpecial_SuperHook"
)


def randomizeItems(thread, level_sarc: SARC) -> None:
    """Iterates through the actors to find item drops and changes what drops"""

    valid_drops = DROPS.copy()
    if not thread.settings['Enemies']:
        del valid_drops["EnemyTakopter"]

    # read banc file which contains the actor list
    file_path = [f.name for f in list(level_sarc.reader.get_files())
                 if f.name.startswith("Banc/")][0]
    banc: BYAML = thread.parent().loadFromSarc(level_sarc, file_path)

    # get all the linked items to be dropped
    linked_ids = []
    for act in banc.info["Actors"]:
        if not thread.thread_active:
            break
        if "Links" in act:
            for link in act["Links"]:
                if link["Name"] == "ToDropItem":
                    linked_ids.append(link["Dst"])

    # iterate through them and change the object type
    # keys need to be left vanilla, so does the infinite zipcaster can in rocket
    for act in banc.info["Actors"]:
        if not thread.thread_active:
            break
        if act["Hash"] not in linked_ids:
            continue
        if act["Name"] in VANILLA_DROPS:
            continue
        new_item = thread.rng.choices(list(valid_drops.keys()), list(valid_drops.values()))[0]
        act["Gyaml"] = new_item
        act["Name"] = new_item
        if new_item == "ItemIkuraBottle":
            act["spl__ItemIkuraBottleBancParam"] = {
                "DropIkuraValue": oead.S32(10),
                "DropNum": oead.S32(10)
            }

    # the new drop objects need unique hashes and instanceid
    ids = {
        "Hash": [[int(h["Hash"]) for h in banc.info["Actors"]]],
        "SRTHash": [[int(h["SRTHash"]) for h in banc.info["Actors"]]],
        "InstanceID": [["".join(h["InstanceID"].split('-')) for h in banc.info["Actors"]]]
    }
    new_drops = []

    # go through the boxes that just gives power eggs and link to new hashes
    # we could do this for balloons, but a lot float over water and would be hard to obtain
    for act in banc.info["Actors"]:
        if not thread.thread_active:
            break
        if "WoodenBox" not in act["Name"] and act["Name"] != "AirBallParent":
            continue
        if "Links" in act:
            continue
        if thread.rng.random() < (1 / 4): # 1/4 chance of no drop
            continue
        act["spl__WoodenBoxBancParam"] = {} # remove egg reward
        act["spl__AirBallBancParam"] = {} # remove egg reward
        new_item = thread.rng.choices(list(valid_drops.keys()), list(valid_drops.values()))[0]
        drop = SplActor(new_item, ids, thread.rng)
        act["Links"] = [{"Name": "ToDropItem", "Dst": oead.U64(drop.hash)}]
        act["spl__ItemDropBancParam"] = {"ToDropItem": oead.U64(drop.hash)}
        if new_item == "ItemIkuraBottle":
            drop.parameters["spl__ItemIkuraBottleBancParam"] = {
                "DropIkuraValue": oead.S32(10),
                "DropNum": oead.S32(10)
            }
        new_drops.append(drop)

    for drop in new_drops:
        banc.info["Actors"].append(drop.pack())

    # save banc file
    thread.parent().saveToSarc(level_sarc, file_path, banc)
