from RandomizerCore.Tools.zs_tools import BYAML, SARC
from randomizer_paths import DATA_PATH
import oead

with open(DATA_PATH / "HeroMode" / "enemies.txt") as f:
    enemy_list = f.read().splitlines()
ENEMIES = [e for e in enemy_list if not e.startswith('#')]


def randomizeEnemies(thread, zs_data: SARC) -> None:
    """Iterates through the list of actors and edits the type and/or size of enemies"""

    banc_file = [str(f) for f in zs_data.reader.get_files() if f.name.endswith(".bcett.byml")][0]
    banc = BYAML(zs_data.writer.files[banc_file])
    for act in banc.info["Actors"]:
        if not thread.thread_active:
            break
        if act["Name"] in ENEMIES:
            if thread.settings["Enemies"]:
                valid_enemies = ENEMIES.copy()
                if "Links" in act: # limit to enemies that support the ToParent link
                    if act["Links"][0]["Name"] == "ToParent":
                        valid_enemies = [e for e in valid_enemies
                                         if e.startswith("Spl")
                                         or "Takolien" in e]
                enemy = thread.rng.choice(valid_enemies)
                while not checkIfEnemyIsValid(thread.rng, act["Name"], enemy):
                    enemy = thread.rng.choice(valid_enemies)
                act["Name"] = enemy
                act["Gyaml"] = enemy
            size = 1.0
            if thread.settings["Enemy Sizes"]:
                size = thread.rng.uniform(0.5, 2.0)
                act["Scale"] = oead.byml.Array([oead.F32(size) for s in range(3)])
            if act["Name"].endswith("Takopter"):
                act["Translate"][1] = oead.F32(float(act["Translate"][1]) + (1.5 * size))
    zs_data.writer.files[banc_file] = banc.repack()


def checkIfEnemyIsValid(rng, name, new_name) -> bool:
    """Checks if the new enemy is valid

    There are a couple general rules that we want to follow to prevent issues like enemies falling to their deaths or locking progression"""

    # vanilla flying enemies need a new flying enemy to replace them
    if name.endswith("Takopter") and not new_name.endswith("Takopter"):
        return False

    # 1/5 enemies in the list have shields. We limit this down to 7%
    if "Shield" in new_name:
        if rng.random() < 0.35:
            return False

    # when the enemy that a barrier is protecting is killed, it flies to the next closest enemy
    # This can lock progression. While not a true softlock, it would still be nice to avoid altogether
    if new_name == "EnemyBarrierTakopter" and name != "EnemyBarrierTakopter":
        return False

    return True
