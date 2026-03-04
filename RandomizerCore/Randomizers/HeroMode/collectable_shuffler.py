from RandomizerCore.Tools.zs_tools import BYAML
from randomizer_paths import DATA_PATH
import oead, yaml

with open(DATA_PATH / "HeroMode" / "collectables.yml", "r") as f:
    COLLECTABLES = yaml.safe_load(f)


class CollectableShuffler:
    def __init__(self, rng):
        self.item_names = [k for k in COLLECTABLES]
        self.items = []
        for item in self.item_names:
            for i in range(COLLECTABLES[item]['count']):
                self.items.append({item: i})
        rng.shuffle(self.items)


    def randomizeCollectables(self, banc: BYAML) -> None:
        """Iterates through the actor list to change the type and index of collectables"""

        for act in banc.info['Actors']:
            if act['Name'] in self.item_names:
                new_item = self.items.pop()
                name = list(new_item.keys())[0]
                id = list(new_item.values())[0]
                act['Gyaml'] = name
                act['Name'] = name
                if COLLECTABLES[name]['needsID']:
                    act['spl__ItemWithPedestalBancParam'] = {'PlacementID': oead.S32(id)}
                else:
                    act['spl__ItemWithPedestalBancParam'] = {}
                    if name == 'ItemIkuraBottle':
                        act['spl__ItemIkuraBottleBancParam'] = {
                            'DropIkuraValue': oead.S32(10),
                            'DropNum': oead.S32(10)
                        }
