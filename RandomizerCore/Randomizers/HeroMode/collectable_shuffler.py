from RandomizerCore.Tools.zs_tools import BYAML
from randomizer_paths import DATA_PATH
import oead, yaml

with open(DATA_PATH / "HeroMode" / "collectables.yml", "r") as f:
    COLLECTABLES = yaml.safe_load(f)


def randomizeCollectables(rng, banc: BYAML) -> None:
    item_names = [k for k in COLLECTABLES]
    items = []
    for item in item_names:
        for i in range(COLLECTABLES[item]['count']):
            items.append({item: i})
    rng.shuffle(items)
    for act in banc.info['Actors']:
        if act['Name'] in item_names:
            new_item = items.pop()
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
