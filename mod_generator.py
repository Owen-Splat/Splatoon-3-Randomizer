from PySide6 import QtCore

import os
import copy
import time
import random
import traceback

import Tools.event_tools as event_tools
import Tools.zs_tools as zs_tools
import oead

from randomizer_data import PARAMS




class ModsProcess(QtCore.QThread):
    
    progress_update = QtCore.Signal(int)
    status_update = QtCore.Signal(str)
    error = QtCore.Signal(str)
    is_done = QtCore.Signal()
    
    
    def __init__(self, rom_path, out_dir, seed, settings, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.rom_path = rom_path
        self.out_dir = out_dir
        random.seed(seed)
        self.settings = settings
        self.progress_value = 0
        self.thread_active = True
        self.levels = {}
        # self.alterna_levels = {}
        # self.crater_levels = {}



    # automatically called when this thread is started
    def run(self):
        try:
            if self.settings['kettles']: self.randomizeKettles()
            self.editLevels()
            if self.thread_active:
                os.mkdir(f'{self.out_dir}/0100C2500FC20000')
        
        except Exception:
            er = traceback.format_exc()
            self.error.emit(er)
        
        finally: # tell the GUI that this thread has finished
            self.is_done.emit()



    def randomizeKettles(self):
        time.sleep(1)
        self.status_update.emit('Randomizing kettles...')

        self.levels['Msn_ExStage'] = 'Msn_ExStage' # restrict After Alterna to vanilla for now to avoid confusion
        levels: list = copy.deepcopy(PARAMS['Missions'])
        random.shuffle(levels)
        for msn in PARAMS['Missions']:
            new_level = ''
            valid_placement = False

            while not valid_placement:
                new_level = random.choice(levels)
                if new_level.endswith('King'): # restrict Alterna bosses to be in Alterna, no more than 1 per site
                    if msn.startswith('Msn_C'):
                        continue
                    else:
                        site = msn[6]
                        bosses = [k for k,v in self.levels.items() if v.endswith('King')]
                        existing_bosses = [b for b in bosses if b[6] == site]
                        if existing_bosses:
                            continue
                
                valid_placement = True
            
            levels.remove(new_level)
            self.levels[msn] = new_level
            self.progress_value += 1
            self.progress_update.emit(self.progress_value)

            # since there is no logic currently, this happens pretty much instantly
            # so we add some delay to give a sense of progression, makes users happy :)
            # this can just be removed when actual logic is written
            time.sleep(0.01)



    # iterate through all level files and randomize the level data
    def editLevels(self):
        time.sleep(1)
        self.status_update.emit('Editing levels...')
        os.makedirs(f'{self.out_dir}/romfs/Pack/Scene')
        
        valid_seasons = [k for k in PARAMS['Main_Weapons'] if int(k[7]) <= self.settings['season']]
        main_weapons_list = []
        for season in valid_seasons:
            for weapon in PARAMS['Main_Weapons'][season]:
                main_weapons_list.append(weapon)
        
        missions = [f for f in os.listdir(f'{self.rom_path}/Pack/Scene') if f.startswith('Msn_')
                    or f.split(".", 1)[0] in ('BigWorld', 'SmallWorld', 'LaunchPadWorld', 'LastBoss', 'LastBoss02', 'StaffRoll')]
        for m in missions:
            if not self.thread_active:
                break
            
            msn = m.split('.', 1)[0]
            
            with open(f'{self.rom_path}/Pack/Scene/{m}', 'rb') as f:
                zs_data = zs_tools.SARC(f.read())
            
            if self.settings['backgrounds']:
                self.randomizeBackground(msn, zs_data)
            
            if msn == 'StaffRoll':
                self.fastCredits(m, zs_data)
                continue
            
            if msn in ('BigWorld', 'SmallWorld'):
                self.editHubs(msn, zs_data)
                        
            # mission info
            info_file = f'SceneComponent/MissionMapInfo/{msn}.spl__MissionMapInfo.bgyml'
            mission_data = zs_tools.BYAML(zs_data.writer.files[info_file])
            
            if self.settings['kettles']:
                self.fixMissionCompatibility(msn, mission_data)
            
            if self.settings['ink-color']:
                mission_data.info['TeamColor'] =\
                    f"Work/Gyml/{random.choice(PARAMS['Colors'])}.game__gfx__parameter__TeamColorDataSet.gyml"
            
            if self.settings['1HKO'] and mission_data.info['MapType'].endswith('Stage'):
                self.addChallenges(mission_data)
            
            if 'OctaSupplyWeaponInfoArray' not in mission_data.info:
                has_weapons = False
            else:
                has_weapons = True
            
            if has_weapons:
                self.randomizeWeapons(mission_data, main_weapons_list)
            
            zs_data.writer.files[info_file] = mission_data.repack()
            
            # scene bgm
            if self.settings['music']:
                self.randomizeMusic(msn, zs_data)
            
            if self.settings['remove-cutscenes']:
                self.removeCutscenes(msn, zs_data)
                        
            with open(f'{self.out_dir}/romfs/Pack/Scene/{m}', 'wb') as f:
                f.write(zs_data.repack())
                self.progress_value += 1
                self.progress_update.emit(self.progress_value)
        
        # with open(f'{self.out_dir}/romfs/RSDB/MissionMapInfo.Product.400.rstbl.byml.zs', 'wb') as f:
        #     f.write(ui_missions_data.repack())
        #     self.progress_value += 1
        #     self.progress_update.emit(self.progress_value)



    def randomizeBackground(self, msn, zs_data):
        if msn[4] == 'C' or 'King' in msn or 'Boss' in msn:
            return
        
        renders = [str(f) for f in zs_data.reader.get_files() if f.name.endswith('RenderingMission.bgyml')]
        if renders:
            render_data = zs_tools.BYAML(zs_data.writer.files[renders[0]])
            sky = random.choice(PARAMS['Backgrounds'])
            render_data.info['Lighting']['SkySphere']['ActorName'] = f'Work/Actor/{sky}.engine__actor__ActorParam.gyml'
            zs_data.writer.files[renders[0]] = render_data.repack()



    def fastCredits(self, m, zs_data):
        if self.settings['remove-cutscenes']:
            flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_StaffRoll.bfevfl'])
            zs_data.writer.files['Event/EventFlow/Mission_StaffRoll.bfevfl'] =\
                self.skipCutscene(flow, 'Event58', 'Event52')
            with open(f'{self.out_dir}/romfs/Pack/Scene/{m}', 'wb') as f:
                f.write(zs_data.repack())
        
        self.progress_value += 1
        self.progress_update.emit(self.progress_value)



    def editHubs(self, msn, zs_data):
        # changes the ChangeSceneName parameters of kettles to the randomized levels
        if self.settings['kettles']:
            banc = zs_tools.BYAML(zs_data.writer.files[f'Banc/{msn}.bcett.byml'])
            for act in banc.info['Actors']:
                if act['Name'] in ('MissionGateway', 'MissionGatewayChallenge', 'MissionBossGateway'):
                    scene = act['spl__MissionGatewayBancParam']['ChangeSceneName']
                    act['spl__MissionGatewayBancParam']['ChangeSceneName'] = self.levels[scene]
            zs_data.writer.files[f'Banc/{msn}.bcett.byml'] = banc.repack()



    def fixMissionCompatibility(self, msn, mission_data):
        if 'King' in msn or 'Boss' in msn:
            return
        
        freebies = (
            self.levels['Msn_A01_01'],
            self.levels['Msn_ExStage'],
            self.levels['Msn_C_01'],
            self.levels['Msn_C_02'],
            self.levels['Msn_C_03'],
            self.levels['Msn_C_04']
        )

        # remove admission fee for levels that should be free
        if msn in freebies and 'Admission' in mission_data.info:
            mission_data.info['Admission'] = oead.S32(0)
        
        # make alterna and crater levels have the correct MapType
        try:
            stage = [k for k,v in self.levels.items() if v == msn][0]
            if stage[4] == 'A':
                mission_data.info['MapType'] = 'ChallengeStage'
            elif stage[4] == 'C':
                mission_data.info['MapType'] = 'SmallWorldStage'
        except IndexError:
            pass # this just means that the stage is not a mission, or is After Alterna. we can ignore this case



    def addChallenges(self, mission_data):
        if 'ChallengeParamArray' in mission_data.info:
            has_sudden_death = False
            for i in range(len(mission_data.info['ChallengeParamArray'])):
                try:
                    if mission_data.info['ChallengeParamArray'][i]['Type'] == 'DamageSuddenDeath':
                        has_sudden_death = True
                except KeyError:
                    break
            if not has_sudden_death:
                mission_data.info['ChallengeParamArray'].append({'Type': 'DamageSuddenDeath'})
        else:
            mission_data.info['ChallengeParamArray'] = [{'Type': 'DamageSuddenDeath'}]



    def randomizeWeapons(self, mission_data, main_weapons_list):
        if len(mission_data.info['OctaSupplyWeaponInfoArray']) > 0:
            while len(mission_data.info['OctaSupplyWeaponInfoArray']) < 3:
                mission_data.info['OctaSupplyWeaponInfoArray'].append(
                    mission_data.info['OctaSupplyWeaponInfoArray'][0])
        
        mains = ['']
        for i in range(len(mission_data.info['OctaSupplyWeaponInfoArray'])):
            e = mission_data.info['OctaSupplyWeaponInfoArray'][i]
            
            if i == 0 and self.settings['beatable']: # leave first option as vanilla
                continue
            
            main_weapon = ''
            while main_weapon in mains:
                main_weapon = random.choice(main_weapons_list)
            mains.append(main_weapon)
            e['WeaponMain'] = f"Work/Gyml/{main_weapon}.spl__WeaponInfoMain.gyml"
            if main_weapon == 'Hero':
                e['SupplyWeaponType'] = 'Hero'
                continue
            
            # sub
            sub_weapon = random.choice(PARAMS['Sub_Weapons'])
            if sub_weapon == 'Free':
                e['SubWeapon'] = ''
            else:
                e['SubWeapon'] = f"Work/Gyml/{sub_weapon}.spl__WeaponInfoSub.gyml"
            
            # special
            if 'SpecialWeapon' in e and any(sp in e['SpecialWeapon'] for sp in ('SpSuperHook_Mission', 'SpJetpack_Mission')):
                if i == 0:
                    continue
            
            special_weapon = random.choice(PARAMS['Special_Weapons'])
            e['SpecialWeapon'] = f"Work/Gyml/{special_weapon}.spl__WeaponInfoSpecial.gyml"
            
            e['SupplyWeaponType'] = 'Normal'
            if main_weapon == 'Free' and sub_weapon == 'Free':
                e['SupplyWeaponType'] = 'Special'
            elif special_weapon in ('SpJetpack_Mission', 'SpGachihoko', 'SpSuperLanding', 'SpUltraStamp_Mission', 'SpChariot_Mission'):
                if random.random() < 0.125: # 1/8 chance for special
                    e['SupplyWeaponType'] = 'Special'
            elif special_weapon == 'SpSuperHook_Mission':
                if random.random() < 0.125:
                    e['SupplyWeaponType'] = 'MainAndSpecial'



    def randomizeMusic(self, msn, zs_data):
        try:
            info_file = f'SceneComponent/SceneBgm/{msn}.spl__SceneBgmParam.bgyml'
            bgm_data = zs_tools.BYAML(zs_data.writer.files[info_file])
        except KeyError:
            # special case where Msn_EX02's SceneBgm isn't named properly like the others
            info_file = f'SceneComponent/SceneBgm/Msn_A01_01.spl__SceneBgmParam.bgyml'
            bgm_data = zs_tools.BYAML(zs_data.writer.files[info_file])
        
        if 'SceneSpecificBgm' in bgm_data.info and '_R_' not in msn:
            bgms = list(copy.deepcopy(PARAMS['Music']))
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
            new_bgm = random.choice(bgms)
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



    def skipCutscene(self, flow, before, after):
        event_tools.insertEventAfter(flow.flowchart, before, after)
        return event_tools.writeFlow(flow)



    def removeCutscenes(self, msn, zs_data):
        # event_files = [str(f) for f in zs_data.reader.get_files() if f.name.endswith('.bfevfl')]

        # make certain flowcharts empty so that cutscenes don't play
        # edit others to just cut to the end
        if msn == 'BigWorld':
            zs_data.writer.files['Event/EventFlow/Mission_IntroduceComrade.bfevfl'] = oead.Bytes()
            zs_data.writer.files['Event/EventFlow/Mission_IntroduceTrinity.bfevfl'] = oead.Bytes()
            zs_data.writer.files['Event/EventFlow/Mission_BigWorldFirst.bfevfl'] = oead.Bytes() # - keep cool wake up cutscene
            zs_data.writer.files['Event/EventFlow/Mission_BigWorldTutorial.bfevfl'] = oead.Bytes()
            zs_data.writer.files['Event/EventFlow/Mission_AfterClearBossStage_0.bfevfl'] = oead.Bytes()
            zs_data.writer.files['Event/EventFlow/Mission_AfterClearBossStage_1.bfevfl'] = oead.Bytes()
            zs_data.writer.files['Event/EventFlow/Mission_AfterClearBossStage_2.bfevfl'] = oead.Bytes()
            
            flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_TreasureMarge.bfevfl'])
            zs_data.writer.files['Event/EventFlow/Mission_TreasureMarge.bfevfl'] =\
                self.skipCutscene(flow, 'EntryPoint0', 'Event49')
            
            flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_DestroyLaunchPadKebaInk.bfevfl'])
            zs_data.writer.files['Event/EventFlow/Mission_DestroyLaunchPadKebaInk.bfevfl'] =\
                self.skipCutscene(flow, 'EntryPoint0', 'Event12')
        
        elif msn == 'SmallWorld':
            # zs_data.writer.files['Event/EventFlow/Mission_SmallWorldFirst.bfevfl'] - INFINITE LOADING SCREEN
            zs_data.writer.files['Event/EventFlow/Mission_SecondStageClear.bfevfl'] = oead.Bytes()
            zs_data.writer.files['Event/EventFlow/Mission_ThirdStageClear.bfevfl'] = oead.Bytes()
            
            flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_AppearSmallWorldBoss.bfevfl'])
            zs_data.writer.files['Event/EventFlow/Mission_AppearSmallWorldBoss.bfevfl'] =\
                self.skipCutscene(flow, 'EntryPoint0', 'Event46')
        
        elif msn == 'Msn_RailKing':
            flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_SmallWorldBossDefeat.bfevfl'])
            zs_data.writer.files['Event/EventFlow/Mission_SmallWorldBossDefeat.bfevfl'] =\
                self.skipCutscene(flow, 'EntryPoint0', 'Event34')
        
        elif msn == 'LaunchPadWorld':
            # not enough time to look into lol
            # flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_TrinityBecomeFriend.bfevfl'])
            # event_tools.insertEventAfter(flow.flowchart, 'Event42', 'Event36')
            # zs_data.writer.files['Event/EventFlow/Mission_TrinityBecomeFriend.bfevfl'] = oead.Bytes()
            
            flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_PrevLastBoss.bfevfl'])
            zs_data.writer.files['Event/EventFlow/Mission_PrevLastBoss.bfevfl'] =\
                self.skipCutscene(flow, 'EntryPoint1', 'Event36')
            
            flow = event_tools.readFlow(zs_data.writer.files['Event/EventFlow/Mission_ReadyForLastBossStage.bfevfl'])
            zs_data.writer.files['Event/EventFlow/Mission_ReadyForLastBossStage.bfevfl'] =\
                self.skipCutscene(flow, 'EntryPoint1', 'Event92')
        else:
            zs_data.writer.files['Event/EventFlow/Mission_BigWorldStageFirst.bfevfl'] = oead.Bytes()



    # STOP THREAD
    def stop(self):
        self.thread_active = False
