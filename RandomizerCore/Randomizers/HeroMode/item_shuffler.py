from RandomizerCore.Tools.zs_tools import BYAML, SARC
import oead, secrets

# we only include one enemy entry because it gets removed if enemies arent randomized
# enemies get randomized after the item drops, so it will turn into a different enemy anyway
DROPS = {
    "ItemArmor": 2.5,
    "ItemCanSpecial_Blower": 0.2,
    "ItemCanSpecial_Chariot": 0.3,
    "ItemCanSpecial_InkStorm": 0.2,
    "ItemCanSpecial_Jetpack": 0.3,
    "ItemCanSpecial_MicroLaser": 0.2,
    "ItemCanSpecial_MultiMissile": 0.2,
    "ItemCanSpecial_ShockSonar": 0.2,
    "ItemCanSpecial_Skewer": 0.2,
    "ItemCanSpecial_SuperHook": 0.3,
    "ItemCanSpecial_SuperLanding": 0.3,
    "ItemCanSpecial_TripleTornado": 0.2,
    "ItemCanSpecial_UltraShot": 0.2,
    "ItemCanSpecial_UltraStamp": 0.2,
    "ItemIkura": 2.5,
    "ItemIkuraBottle": 5.0,
    # "ItemIkuraLarge": 4.0,
    # "ItemInkBottle": 2.0, # seems to crash the game
    "EnemyTakopter": 4.0
}


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
    # keys need to be left vanilla
    for act in banc.info["Actors"]:
        if not thread.thread_active:
            break
        if act["Hash"] not in linked_ids:
            continue
        if act["Name"] == "ItemCardKey":
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
        if "WoodenBox" not in act["Name"]:
            continue
        if "Links" in act:
            continue
        if thread.rng.random() < (1 / 3): # 1/3 chance of no drop
            continue
        act["spl__WoodenBoxBancParam"] = {} # remove egg reward
        new_item = thread.rng.choices(list(valid_drops.keys()), list(valid_drops.values()))[0]
        drop = DropItem(new_item, ids, thread.rng)
        act["Links"] = [{"Name": "ToDropItem", "Dst": oead.U64(drop.hash)}]
        act["spl__ItemDropBancParam"] = {"ToDropItem": oead.U64(drop.hash)}
        new_drops.append(drop)

    for drop in new_drops:
        banc.info["Actors"].append(drop.pack())

    # save banc file
    thread.parent().saveToSarc(level_sarc, file_path, banc)


# Code taken from my old Splatoon 3 Only Up level creation code
class DropItem:
    """Represents a Splatoon 3 actor object"""

    def __init__(self, name: str, ids: dict, rng):
        self.name = name
        self.translate = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]
        self.team = "Neutral"
        if name.startswith("Enemy"):
            self.team = "Bravo"

        # create unique IDs for the object
        hash = rng.getrandbits(64)
        while hash in ids["Hash"]:
            hash = rng.getrandbits(64)
        ids["Hash"].append(hash)
        self.hash = hash

        srt_hash = rng.getrandbits(32)
        while srt_hash in ids["SRTHash"]:
            srt_hash = rng.getrandbits(32)
        ids["SRTHash"].append(srt_hash)
        self.srt_hash = srt_hash

        instance_id = secrets.token_hex(16)
        while instance_id in ids["InstanceID"]:
            instance_id = secrets.token_hex(16)
        ids["InstanceID"].append(instance_id)
        self.instance_id = instance_id


    def pack(self) -> dict:
        """Converts this object into a dict with oead typings"""

        objd = {}

        objd["Name"] = self.name
        objd["Gyaml"] = self.name
        objd["Hash"] = oead.U64(self.hash)
        objd["SRTHash"] = oead.U32(self.srt_hash)
        objd["InstanceID"] = f"{self.instance_id[:8]}-{self.instance_id[8:12]}-{self.instance_id[12:16]}-{self.instance_id[16:20]}-{self.instance_id[20:]}"
        objd["Phive"] = {"Placement": {"ID": oead.U64(self.hash)}}
        # if self.rotation != [0.0, 0.0, 0.0]: # convert rotation to radians if the field is needed
        #     objd['Rotate'] = oead.byml.Array([oead.F32(r * 3.141592 / 180) for r in self.rotation])
        objd["Scale"] = oead.byml.Array([oead.F32(s) for s in self.scale])
        objd["TeamCmp"] = {"Team": self.team}
        objd["Translate"] = oead.byml.Array([oead.F32(t) for t in self.translate])

        if self.name == "ItemIkuraBottle":
            objd["spl__ItemIkuraBottleBancParam"] = {
                "DropIkuraValue": oead.S32(10),
                "DropNum": oead.S32(10)
            }
        
        return objd
