from RandomizerCore.Tools.zs_tools import BYAML, SARC
from randomizer_paths import DATA_PATH
import oead

with open(DATA_PATH / "HeroMode" / "enemies.txt") as f:
    enemy_list = f.read().splitlines()
ENEMIES = [e for e in enemy_list if not e.startswith('#')]


def randomizeEnemies(thread, zs_data: SARC) -> None:
    banc_file = [str(f) for f in zs_data.reader.get_files() if f.name.endswith('.bcett.byml')][0]
    banc = BYAML(zs_data.writer.files[banc_file])
    for act in banc.info['Actors']:
        if not thread.thread_active:
            break
        if act['Name'] in ENEMIES:
            if thread.settings['Enemies']:
                enemy = thread.rng.choice(ENEMIES)
                while 'Shield' in enemy: # 1/5 enemies will be shielded so lets trim that down
                    if thread.rng.randint(1, 2) == 2:
                        break
                    enemy = thread.rng.choice(ENEMIES)
                act['Name'] = enemy
                act['Gyaml'] = enemy
            size = 1.0
            if thread.settings['Enemy Sizes']:
                size = thread.rng.uniform(0.5, 2.0)
                act['Scale'] = oead.byml.Array([oead.F32(size) for s in range(3)])
            if enemy.endswith('Takopter'):
                act['Translate'][1] = oead.F32(float(act['Translate'][1]) + (1.5 * size))
    zs_data.writer.files[banc_file] = banc.repack()
