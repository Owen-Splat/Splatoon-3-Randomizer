import oead, secrets


# Code taken from my old Splatoon 3 Only Up level creation code
class SplActor:
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
