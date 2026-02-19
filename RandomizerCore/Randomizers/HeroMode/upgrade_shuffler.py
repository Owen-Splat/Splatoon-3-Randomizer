from RandomizerCore.Tools.zs_tools import BYAML, SARC
from randomizer_paths import DATA_PATH

with open(DATA_PATH / "HeroMode" / "upgrades.txt", "r") as f:
    UPGRADES = f.read().splitlines()


def randomizeUpgrades(rng, zs_data: SARC) -> None:
    """Shuffles the hero upgrades around"""

    skills = UPGRADES.copy()
    rng.shuffle(skills)
    skill_file = 'Gyml/Singleton/spl__MissionConstant.spl__MissionConstant.bgyml'
    skill_table = BYAML(zs_data.writer.files[skill_file])
    for skill in skill_table.info['PlayerSkillTree']['SkillIconTable']:
        new_skill = rng.choice(skills)
        skills.remove(new_skill)
        skill['SkillType'] = new_skill
        if new_skill == 'HeroShotUp':
            del skill['SkillType']
    zs_data.writer.files[skill_file] = skill_table.repack()
