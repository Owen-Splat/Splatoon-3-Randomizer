from RandomizerCore.Tools.zs_tools import BYAML
from randomizer_paths import DATA_PATH
import time

with open(DATA_PATH / "HeroMode" / "missions.txt", "r") as f:
    MISSIONS = f.read().splitlines()


def randomizeLevels(thread) -> dict:
    """Creates a dict of randomized levels, the key is the old level and the value is the new level"""

    # Update the ui status and add a slight delay so that the user has time to read it
    thread.status_update.emit('Randomizing levels...')
    time.sleep(1)

    crater_missions = [c for c in MISSIONS if "_C_" in c]
    alterna_missions = [a for a in MISSIONS if a not in crater_missions]

    levels = {}

    # restrict After Alterna to vanilla for now to avoid confusion
    levels['Msn_ExStage'] = 'Msn_ExStage'

    # C-1 needs to be vanilla to allow the player to use Smallfry
    # C-1 -> C-4 all need to be beaten for the Octavio ooze
    # So all Crater levels need to stay in the Crater, and C-1 stays vanilla
    levels['Msn_C_01'] = 'Msn_C_01'

    c_levels = [c for c in crater_missions if c not in levels]
    a_levels = [a for a in alterna_missions if a not in levels]
    b_levels = [b for b in a_levels if b.endswith('King')]
    thread.rng.shuffle(c_levels)
    thread.rng.shuffle(a_levels)
    thread.rng.shuffle(b_levels)

    for msn in crater_missions:
        if not thread.thread_active:
            break
        if msn in levels:
            continue
        new_level = thread.rng.choice(c_levels)
        c_levels.remove(new_level)
        levels[msn] = new_level
    
    boss_sites = []
    while b_levels:
        new_level = thread.rng.choice(a_levels)
        if new_level in levels or new_level[6] in boss_sites:
            continue
        boss_sites.append(new_level[6])
        boss = b_levels.pop()
        a_levels.remove(boss)
        levels[new_level] = boss
    
    for msn in alterna_missions:
        if not thread.thread_active:
            break
        if msn in levels:
            continue
        new_level = thread.rng.choice(a_levels)
        a_levels.remove(new_level)
        levels[msn] = new_level

    return levels


def changeKettleDestinations(banc: BYAML, levels: dict) -> None:
    """Changes the ChangeSceneName parameter of each kettle to the randomized levels"""

    for act in banc.info['Actors']:
        if act['Name'] in ('MissionGateway', 'MissionGatewayChallenge', 'MissionBossGateway'):
            scene = act['spl__MissionGatewayBancParam']['ChangeSceneName']
            act['spl__MissionGatewayBancParam']['ChangeSceneName'] = levels[scene]
