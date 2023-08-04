from PySide6 import QtCore

import os
import copy
import random
import traceback

import Tools.zs_tools as zs_tools
import oead

from randomizer_data import PARAMS




class ModsProcess(QtCore.QThread):
    
    progress_update = QtCore.Signal(int)
    is_done = QtCore.Signal()
    error = QtCore.Signal(str)

    
    def __init__(self, rom_path, out_dir, seed, settings, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.rom_path = rom_path
        self.out_dir = out_dir
        random.seed(seed)
        self.settings = settings
        self.progress_value = 0
        self.thread_active = True    



    # automatically called when this thread is started
    def run(self):
        try:
            self.randomizeLevels()
            if self.thread_active:
                os.mkdir(f'{self.out_dir}/0100C2500FC20000')
        
        except Exception:
            er = traceback.format_exc()
            self.error.emit(er)
        
        finally: # tell the GUI that this thread has finished
            self.is_done.emit()


    # iterate through all level files and randomize the level data
    def randomizeLevels(self):
        os.makedirs(f'{self.out_dir}/romfs/Pack/Scene')
        
        if self.settings['kettles']:
            levels_dict = {}
            crater_levels_dict = {}
            levels = copy.deepcopy(PARAMS['Alterna_Missions'])
            crater_levels = copy.deepcopy(PARAMS['Crater_Missions'])
            random.shuffle(levels)
            random.shuffle(crater_levels)
            
            for msn in PARAMS['Alterna_Missions']:
                if msn in ('Msn_A01_01', 'Msn_ExStage'):
                    new_level = ''
                    while new_level in ('', 'Msn_ExStage') or new_level.endswith('King'):
                        new_level = random.choice(levels)
                    levels_dict[msn] = new_level
                    levels.remove(new_level)
                else:
                    levels_dict[msn] = levels.pop(0)
            for msn in PARAMS['Crater_Missions']:
                crater_levels_dict[msn] = crater_levels.pop(0)
        
        main_weapons_list = copy.deepcopy(PARAMS['Main_Weapons'])
        if not self.settings['grizzco']:
            main_weapons_list = [m for m in PARAMS['Main_Weapons'] if not m.endswith('Bear_Coop')]
        
        missions = [f for f in os.listdir(f'{self.rom_path}/Pack/Scene') if f.startswith('Msn_')
                    or f.split(".", 1)[0] in ('BigWorld', 'SmallWorld', 'LaunchPadWorld', 'LastBoss', 'LastBoss02')]
        for m in missions:
            if not self.thread_active:
                break

            msn = m.split('.', 1)[0]

            with open(f'{self.rom_path}/Pack/Scene/{m}', 'rb') as f:
                zs_data = zs_tools.SARC(f.read())
            
            # shuffle kettles
            if self.settings['kettles'] and msn in ('BigWorld', 'SmallWorld'):
                if msn == 'BigWorld':
                    world_levels_dict = levels_dict
                else:
                    world_levels_dict = crater_levels_dict
                banc = zs_tools.BYAML(zs_data.writer.files[f'Banc/{msn}.bcett.byml'])
                for act in banc.info['Actors']:
                    if act['Name'] in ('MissionGateway', 'MissionGatewayChallenge', 'MissionBossGateway'):
                        scene = act['spl__MissionGatewayBancParam']['ChangeSceneName']
                        act['spl__MissionGatewayBancParam']['ChangeSceneName'] = world_levels_dict[scene]
                zs_data.writer.files[f'Banc/{msn}.bcett.byml'] = banc.repack()
            
            # mission info
            info_file = f'SceneComponent/MissionMapInfo/{msn}.spl__MissionMapInfo.bgyml'
            mission_data = zs_tools.BYAML(zs_data.writer.files[info_file])
            
            # make 1-1 and AA have no entrance fee so they can be played immediately
            if msn in (levels_dict['Msn_A01_01'], levels_dict['Msn_ExStage']):
                if 'Admission' in mission_data.info:
                    mission_data.info['Admission'] = oead.S32(0)
            
            if self.settings['ink-color']:
                mission_data.info['TeamColor'] =\
                    f"Work/Gyml/{random.choice(PARAMS['Colors'])}.game__gfx__parameter__TeamColorDataSet.gyml"
            
            if self.settings['1HKO'] and mission_data.info['MapType'].endswith('Stage'):
                mission_data.info['MapType'] = 'ChallengeStage'
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
            
            if 'OctaSupplyWeaponInfoArray' not in mission_data.info:
                has_weapons = False
            else:
                has_weapons = True
            
            if has_weapons:
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
                    
                    # sub
                    if self.settings['beatable'] and 'SubWeapon' in e:
                        sub_weapon = e['SubWeapon']
                    else:
                        sub_weapon = random.choice(PARAMS['Sub_Weapons'])
                        if sub_weapon == 'Free':
                            e['SubWeapon'] = ''
                        else:
                            e['SubWeapon'] = f"Work/Gyml/{sub_weapon}.spl__WeaponInfoSub.gyml"
                    
                    # special
                    if 'SpecialWeapon' in e and any(sp in e['SpecialWeapon'] for sp in ('SpSuperHook_Mission', 'SpJetpack_Mission')):
                        special_weapon = e['SpecialWeapon']
                        continue
                    else:
                        special_weapon = random.choice(PARAMS['Special_Weapons'])
                        e['SpecialWeapon'] = f"Work/Gyml/{special_weapon}.spl__WeaponInfoSpecial.gyml"
                    
                    e['SupplyWeaponType'] = 'Normal'
                    if main_weapon == 'Free' and sub_weapon == 'Free':
                        e['SupplyWeaponType'] = 'Special'
                    elif special_weapon in ('SpJetpack_Mission', 'SpGachihoko', 'SpSuperLanding', 'SpUltraStamp_Mission'):
                        if random.random() < 0.2: # 1/5 chance for special
                            e['SupplyWeaponType'] = 'Special'
                    if special_weapon == 'SpSuperHook_Mission':
                        e['SupplyWeaponType'] = 'MainAndSpecial'
            
            zs_data.writer.files[info_file] = mission_data.repack()

            # scene bgm
            if self.settings['music']:
                try:
                    info_file = f'SceneComponent/SceneBgm/{msn}.spl__SceneBgmParam.bgyml'
                    bgm_data = zs_tools.BYAML(zs_data.writer.files[info_file])
                except KeyError:
                    # special case where Msn_EX02's SceneBgm isn't named properly like the others
                    info_file = f'SceneComponent/SceneBgm/Msn_A01_01.spl__SceneBgmParam.bgyml'
                    bgm_data = zs_tools.BYAML(zs_data.writer.files[info_file])
                
                if 'SceneSpecificBgm' in bgm_data.info and '_R_' not in msn:
                    new_bgm = random.choice(PARAMS['Music'])
                    bgm_data.info['SceneSpecificBgm'] = new_bgm
                    # if 'Rocket' in new_bgm:
                    #     bgm_data.info['MainController'] = {}
                    #     bgm_data.info['SceneBridgeController'] = {
                    #         'ClassName': 'spl__BgmMissionRocketSceneBridge',
                    #         'SLinkUserName': 'BgmMissionRocketSceneBridge'
                    #     }
                    if '_Boss_' in new_bgm:
                        bgm_data.info['MainController'] = {
                            'ClassName': 'spl__BgmMissionBoss',
                            'SLinkUserName': 'BgmMissionBoss'
                        }
                    elif 'Kumasan' in new_bgm:
                        bgm_data.info['MainController'] = {
                            'ClassName': 'spl__BgmMissionLastBoss',
                            'SLinkUserName': 'BgmMissionLastBoss'
                        }
                        bgm_data.info['SceneBridgeController'] = {
                            'ClassName': 'spl__BgmMissionSceneBridge',
                            'SLinkUserName': 'BgmMissionSceneBridge'
                        }
                    else:
                        bgm_data.info['MainController'] = {
                            'ClassName': 'spl__BgmMissionStage',
                            'SLinkUserName': 'BgmMissionStage'
                        }
                        bgm_data.info['SceneBridgeController'] = {
                            'ClassName': '',
                            'SLinkUserName': ''
                        }
                    zs_data.writer.files[info_file] = bgm_data.repack()

            with open(f'{self.out_dir}/romfs/Pack/Scene/{m}', 'wb') as f:
                f.write(zs_data.repack())
                self.progress_value += 1
                self.progress_update.emit(self.progress_value)



    # STOP THREAD
    def stop(self):
        self.thread_active = False
