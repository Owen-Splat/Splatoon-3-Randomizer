from RandomizerCore.Tools.zs_tools import BYAML, SARC
from randomizer_paths import DATA_PATH

with open(DATA_PATH / "HeroMode" / "music.txt", "r") as f:
    music_list = f.read().splitlines()
MUSIC = [m for m in music_list if not m.startswith('#')]


# TODO: Fix any case where music might not play in a level. Also try to get non-mission songs to play
def randomizeMusic(rng, msn: str, zs_data: SARC) -> None:
    """Assigns a new BGM to the level

    The music stays relative to the level type (e.g. boss songs in bosses)"""

    try:
        info_file = f'SceneComponent/SceneBgm/{msn}.spl__SceneBgmParam.bgyml'
        bgm_data = BYAML(zs_data.writer.files[info_file])
    except KeyError:
        # special case where Msn_EX02's SceneBgm isn't named properly like the others
        info_file = f'SceneComponent/SceneBgm/Msn_A01_01.spl__SceneBgmParam.bgyml'
        bgm_data = BYAML(zs_data.writer.files[info_file])

    if 'SceneSpecificBgm' in bgm_data.info and '_R_' not in msn:
        bgms = MUSIC
        if 'King' in msn: # shuffle boss music within bosses
            bgms = ('BGM_Mission_Boss_Fuuka',
                    'BGM_Mission_Boss_Mantaro',
                    'BGM_Mission_Boss_Takowasa',
                    'BGM_Mission_Boss_Utsuho')
        elif '_R_' in msn: # shuffle rocket music within rocket
            bgms = ('BGM_Mission_Stage_Rocket_01',
                    'BGM_Mission_Stage_Rocket_02',
                    'BGM_Mission_Stage_Rocket_03',
                    'BGM_Mission_Stage_Rocket_04')
        new_bgm = rng.choice(bgms)
        bgm_data.info['SceneSpecificBgm'] = new_bgm
        # if 'Rocket' in new_bgm:
        #     bgm_data.info['MainController'] = {}
        #     bgm_data.info['SceneBridgeController'] = {
        #         'ClassName': 'spl__BgmMissionRocketSceneBridge',
        #         'SLinkUserName': 'BgmMissionRocketSceneBridge'
        #     }
        # if '_Boss_' in new_bgm:
        #     bgm_data.info['MainController'] = {
        #         'ClassName': 'spl__BgmMissionBoss',
        #         'SLinkUserName': 'BgmMissionBoss'
        #     }
        # elif 'Kumasan' in new_bgm:
        #     bgm_data.info['MainController'] = {
        #         'ClassName': 'spl__BgmMissionLastBoss',
        #         'SLinkUserName': 'BgmMissionLastBoss'
        #     }
        #     bgm_data.info['SceneBridgeController'] = {
        #         'ClassName': 'spl__BgmMissionSceneBridge',
        #         'SLinkUserName': 'BgmMissionSceneBridge'
        #     }
        # else:
        #     bgm_data.info['MainController'] = {
        #         'ClassName': 'spl__BgmMissionStage',
        #         'SLinkUserName': 'BgmMissionStage'
        #     }
        #     bgm_data.info['SceneBridgeController'] = {
        #         'ClassName': '',
        #         'SLinkUserName': ''
        #     }
        zs_data.writer.files[info_file] = bgm_data.repack()
