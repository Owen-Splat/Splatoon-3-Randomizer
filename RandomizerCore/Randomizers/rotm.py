from PySide6 import QtCore
from randomizer_data import PARAMS, LOGIC
from pathlib import Path
import RandomizerCore.Tools.event_tools as event_tools
import RandomizerCore.Tools.text_tools as text_tools
import RandomizerCore.Tools.zs_tools as zs_tools
import copy, oead, random, time, traceback



class RotM_Process(QtCore.QThread):
    status_update = QtCore.Signal(str)
    error = QtCore.Signal(str)
    is_done = QtCore.Signal()


    def __init__(self, parent, settings: dict):
        QtCore.QThread.__init__(self, parent)
        self.rom_path = Path(settings['RomFS'])
        self.out_dir = Path(settings['Output'])
        random.seed(settings['Seed'])
        self.settings = dict(settings['HeroMode'])
        self.thread_active = True


    # automatically called when this thread is started
    def run(self):
        try:
            # Make paths before making any edits
            (self.out_dir / 'Pack' / 'Scene').mkdir(parents=True, exist_ok=True)
            (self.out_dir / 'RSDB').mkdir(parents=True, exist_ok=True)
            (self.out_dir / 'Mals').mkdir(parents=True, exist_ok=True)

            # Store the game version based on the provided romfs
            self.version = self.getGameVersion()

            # makes a dict of old levels and the new level that will replace it
            self.levels = {}
            if self.settings['Levels']:
                self.levels = self.randomizeLevels()

            # makes a dict of levels and weapon choices, each level is given 3 choices in increasing difficulty
            self.weapon_placements = {}
            if self.settings['Weapons']:
                self.weapon_placements = self.randomizeWeaponsWithLogic()

            self.editLevels()
            self.updateMissionParameters()
            self.randomizeText()
        
        except Exception:
            er = traceback.format_exc()
            self.error.emit(er)
        
        finally:
            self.is_done.emit()


    def getGameVersion(self) -> str:
        """Get the version string from the RSDB folder in the RomFS

        In the case of the user having dumped multiple updates into the same directory, get the highest one"""

        rsdb_path = self.rom_path / "RSDB"
        markers = [int(f.stem.split('.')[2], 16) for f in rsdb_path.iterdir() if f.stem.startswith("ActorInfo")]
        version_string = hex(max(markers))[2:].lower()
        return version_string


    def randomizeLevels(self) -> dict:
        """Creates a dict of randomized levels, the key is the old level and the value is the new level"""

        # Update the ui status and add a slight delay so that the user has time to read it
        self.status_update.emit('Randomizing levels...')
        time.sleep(1)

        levels = {}

        # restrict After Alterna to vanilla for now to avoid confusion
        levels['Msn_ExStage'] = 'Msn_ExStage'

        # C-1 needs to be vanilla to allow the player to use Smallfry
        # C-1 -> C-4 all need to be beaten for the Octavio ooze
        # So all Crater levels need to stay in the Crater, and C-1 stays vanilla
        levels['Msn_C_01'] = 'Msn_C_01'

        c_levels = [c for c in copy.deepcopy(PARAMS['Crater_Missions']) if c not in levels]
        a_levels = [a for a in copy.deepcopy(PARAMS['Alterna_Missions']) if a not in levels]
        b_levels = [b for b in a_levels if b.endswith('King')]
        random.shuffle(c_levels)
        random.shuffle(a_levels)
        random.shuffle(b_levels)

        for msn in PARAMS['Crater_Missions']:
            if not self.thread_active:
                break
            if msn in levels:
                continue
            new_level = random.choice(c_levels)
            c_levels.remove(new_level)
            levels[msn] = new_level
        
        boss_sites = []
        while b_levels:
            new_level = random.choice(a_levels)
            if new_level in levels or new_level[6] in boss_sites:
                continue
            boss_sites.append(new_level[6])
            boss = b_levels.pop()
            a_levels.remove(boss)
            levels[new_level] = boss
        
        for msn in PARAMS['Alterna_Missions']:
            if not self.thread_active:
                break
            if msn in levels:
                continue
            new_level = random.choice(a_levels)
            a_levels.remove(new_level)
            levels[msn] = new_level

        return levels


    def randomizeWeaponsWithLogic(self) -> dict:
        """Creates a dict of levels and weapon choices. Each level is given 3 choices in increasing difficulty

        Currently, the difficulty is just the weapon type (main, sub, special)"""

        # Update the ui status and add a slight delay so that the user has time to read it
        self.status_update.emit("Randomizing weapons...")
        time.sleep(1)

        weapon_placements = {}

        # Now get the season corresponding to the version. This is just the major version marker besides 1.0.0 which is season 0
        match self.version:
            case "100":
                season = 0
            case _: # default
                season = int(self.version[0], 16)

        # Now use the season to get all the valid weapons listed in our PARAMS file
        valid_seasons = [k for k in PARAMS['Main_Weapons'] if int(k[-1]) <= season]
        main_weapons_list = []
        for season in valid_seasons:
            for weapon in PARAMS['Main_Weapons'][season]:
                main_weapons_list.append(weapon)

        # Now for each level in the logic file, randomly assign 3 weapon choices in increasing difficulty
        # If any are not valid for the given level, reroll
        for k,v in LOGIC["Missions"].items():
            if not self.thread_active:
                break
            weapons = []
            for i in range(3):
                if not self.thread_active:
                    break
                if (not str(k).endswith('C')) and (i == 0): # keep hero weapon choice since the hero weapon is randomized
                    weapons.append("Hero")
                    continue
                w = self.assignWeapon(main_weapons_list, i)
                while not self.checkIfWeaponIsValid(w, v):
                    w = self.assignWeapon(main_weapons_list, i)
                weapons.append(w)
            weapon_placements[f"Msn_{k}"] = weapons

        return weapon_placements

    # TODO: MAKE SURE THE USER DOES NOT GET REPEAT WEAPON CHOICES
    def assignWeapon(self, main_weapons: list, index: int) -> str:
        """Assigns a random weapon of difficulty index with no regard of the level logic"""

        # Since we are using index as the difficulty, add one so we dont multiply by 0
        # This gives us a difficulty rating of 1-3
        difficulty = index + 1

        # Add a chance for special with the chance decreasing based on the difficulty value
        # Since we reroll if the weapon is not valid, there will be more rolls so odds are technically higher
        # 1/8 -> 1/12 -> 1/16
        odds = 8
        odds += 4 * (difficulty - 1)
        special = ""
        if random.random() < (1 / odds):
            special = random.choice(PARAMS["Special_Weapons"])
            if special != "SpSuperHook_Mission":
                return special

        # Determine the weight of each class in regards to the difficulty value
        # This will be reformatted into something more readable, but this is fine for testing what weapons are typically easier or harder 
        class_weights = {
            "Shooter": 4 - difficulty,
            "Blaster": 3 / difficulty,
            "Roller": 3 / difficulty,
            "Brush": 3 / difficulty,
            "Charger": 4 - difficulty,
            "Slosher": 3 / difficulty,
            "Spinner": 4 - difficulty,
            "Maneuver": 4 - difficulty,
            "Shelter": 0.5 + (difficulty - 1),
            "Stringer": 4 - difficulty,
            "Saber": 0.5 + (difficulty - 1),
            "Free": 0 + ((difficulty - 1) * 2)
        }

        # Now make a dict of the weapon names with the class difficulty
        mains_with_weights = {}
        for m in main_weapons:
            if not self.thread_active:
                break
            for k,v in class_weights.items():
                if not self.thread_active:
                    break
                if m.startswith(k):
                    mains_with_weights[m] = v
                    break

        # Now get a random main weapon using the weights
        main = random.choices(list(mains_with_weights.keys()), list(mains_with_weights.values()))[0]
        if special:
            result = f"{special}+{main}"
            return result

        # Now we do the same for sub weapons
        # Besides just difficulty, we need to ensure that we attempt to give a proper bomb if the main weapon is empty
        has_main = True if main == "Free" else False
        sub_weights = {
            "Beacon": difficulty * has_main,
            "Bomb_Curling_Mission": 4 - difficulty,
            "Bomb_Fizzy": 3 / difficulty,
            "Bomb_Quick_Mission": 4 - difficulty,
            "Bomb_Robot_Mission": 4 - difficulty,
            "Bomb_Splash_Mission": 4 - difficulty,
            "Bomb_Suction_Mission": 4 - difficulty,
            "Bomb_Torpedo": 3 / difficulty,
            "LineMarker": 0.5 + (difficulty - 1),
            "PointSensor": difficulty * has_main,
            "PoisonMist": difficulty * has_main,
            "SalmonBuddy": 3 / difficulty,
            "Shield": difficulty * has_main,
            "Sprinkler": difficulty * has_main,
            "Trap_Mission": 3 / difficulty,
            "Free": difficulty * has_main
        }
        sub = random.choices(list(sub_weights.keys()), list(sub_weights.values()))[0]

        result = f"{main}+{sub}"
        return result


    def checkIfWeaponIsValid(self, weapon: str, level_logic: dict) -> bool:
        """Checks if the randomly assigned weapon is valid against the level logic"""

        result = True

        # Unique case where the level is designed around curling bomb
        if "Sub" in level_logic:
            if not weapon.endswith(level_logic["Sub"]):
                result = False

        # Special
        if weapon.startswith("Sp") and not weapon.startswith("Spinner"):
            special = weapon.split('+')[0]
            weapon_logic = LOGIC["Special_Weapons"][special]
            if weapon_logic["Range"] < level_logic["Range"]:
                result = False
            if (not weapon_logic["Floor_Paint"]) and (level_logic["Floor_Paint"]):
                result = False
            if (not weapon_logic["Wall_Paint"]) and (level_logic["Wall_Paint"]):
                result = False
            if (not weapon_logic["Rail"]) and (level_logic["Rail"]):
                result = False
            return result

        # Main + Sub
        if '+' in weapon:
            main, sub = weapon.split('+')
            main_parts = main.split('_')
            main_without_last = main_parts[:-1]
            main = "_".join(main_without_last)
            main_logic = LOGIC["Main_Weapons"][main]
            sub_logic = LOGIC["Sub_Weapons"][sub]
            if main_logic["Range"] < level_logic["Range"]:
                if sub_logic["Range"] < level_logic["Range"]:
                    result = False
            if main == "Free": # all main weapons can paint floor and walls, so if main is nothing, check sub ability to paint
                if (not sub_logic["Floor_Paint"]) and (level_logic["Floor_Paint"]):
                    result = False
                if (not sub_logic["Wall_Paint"]) and (level_logic["Wall_Paint"]):
                    result = False
            if level_logic["Attack"]:
                if not sub_logic["Attack"]:
                    result = False
            return result

        # Main only
        weapon_parts = weapon.split('_')
        weapon_without_last = weapon_parts[:-1]
        weapon = "_".join(weapon_without_last)
        main_logic = LOGIC["Main_Weapons"][weapon]
        if main_logic["Range"] < level_logic["Range"]: # this covers no weapon
            result = False

        return result


    # iterate through all level files and randomize the level data
    def editLevels(self):
        self.status_update.emit('Editing Hero Mode levels...')
        time.sleep(1)

        ui_info_file = [f.name for f in (self.rom_path / 'RSDB').iterdir() if f.name.startswith('MissionMapInfo') and f.name.split('.')[2] == self.version][0]
        with open(self.rom_path / 'RSDB' / ui_info_file, 'rb') as f:
            ui_missions_data = zs_tools.BYAML(f.read(), compressed=True)

        missions = [f.name for f in (self.rom_path / 'Pack' / 'Scene').iterdir() if f.name.startswith('Msn_')
                    or f.name.split('.', 1)[0] in ('BigWorld', 'SmallWorld', 'LaunchPadWorld', 'LastBoss', 'LastBoss02')]
        for m in missions:
            if not self.thread_active:
                break

            msn = m.split('.', 1)[0]

            with open(self.rom_path / 'Pack' / 'Scene' / m, 'rb') as f:
                zs_data = zs_tools.SARC(f.read())

            if self.settings['Backgrounds']:
                self.randomizeBackground(msn, zs_data)

            if msn in ('BigWorld', 'SmallWorld'):
                self.editHubs(msn, zs_data)

            # mission info
            info_file = f'SceneComponent/MissionMapInfo/{msn}.spl__MissionMapInfo.bgyml'
            mission_data = zs_tools.BYAML(zs_data.writer.files[info_file])

            if self.settings['Levels']:
                self.fixMissionCompatibility(msn, mission_data)

            if self.settings['Ink Colors']:
                mission_data.info['TeamColor'] =\
                    f"Work/Gyml/{random.choice(PARAMS['Colors'])}.game__gfx__parameter__TeamColorDataSet.gyml"

            if self.settings['Enemy Ink Is Lava'] and mission_data.info['MapType'].endswith('Stage'):
                self.addChallenges(mission_data)

            has_weapons = True if 'OctaSupplyWeaponInfoArray' in mission_data.info else False
            if has_weapons and self.settings['Weapons']:
                self.editWeaponChoices(msn, mission_data, ui_missions_data)

            zs_data.writer.files[info_file] = mission_data.repack()

            # scene bgm
            if self.settings['Music']:
                self.randomizeMusic(msn, zs_data)

            if self.settings['Skip Cutscenes']:
                self.removeCutscenes(zs_data)

            if self.settings['Enemies'] or self.settings['Enemy Sizes']:
                self.randomizeEnemies(zs_data)

            with open(self.out_dir / 'Pack' / 'Scene' / m, 'wb') as f:
                f.write(zs_data.repack())

        with open(self.out_dir / 'RSDB' / ui_info_file, 'wb') as f:
            f.write(ui_missions_data.repack())


    def randomizeBackground(self, msn, zs_data: zs_tools.SARC):
        if msn[4] == 'C' or 'King' in msn or 'Boss' in msn:
            return

        renders = [str(f) for f in zs_data.reader.get_files() if f.name.endswith('RenderingMission.bgyml')]
        if renders:
            render_data = zs_tools.BYAML(zs_data.writer.files[renders[0]])
            sky = random.choice(PARAMS['Backgrounds'])
            render_data.info['Lighting']['SkySphere']['ActorName'] = f'Work/Actor/{sky}.engine__actor__ActorParam.gyml'
            zs_data.writer.files[renders[0]] = render_data.repack()


    def editHubs(self, msn, zs_data:zs_tools.SARC):
        banc = zs_tools.BYAML(zs_data.writer.files[f'Banc/{msn}.bcett.byml'])

        # changes the ChangeSceneName parameters of kettles to the randomized levels
        if self.settings['Levels']:
            for act in banc.info['Actors']:
                if act['Name'] in ('MissionGateway', 'MissionGatewayChallenge', 'MissionBossGateway'):
                    scene = act['spl__MissionGatewayBancParam']['ChangeSceneName']
                    act['spl__MissionGatewayBancParam']['ChangeSceneName'] = self.levels[scene]

        if msn == 'BigWorld' and self.settings['Fuzzy Ooze Costs']:
            ooze_costs = []
            for i in range(2):
                has_costs = len(ooze_costs) > 0
                for act in banc.info['Actors']:
                    if act['Name'].startswith('KebaInkCore'):
                        if has_costs:
                            act['spl__KebaInkCoreBancParam']['NecessarySalmonRoe'] = ooze_costs[random.randrange(len(ooze_costs))]
                        else:
                            ooze_costs.append(act['spl__KebaInkCoreBancParam']['NecessarySalmonRoe'])

        if self.settings['Collectables']:
            item_names = [k for k in PARAMS['Collectables']]
            items = []
            for item in item_names:
                for i in range(PARAMS['Collectables'][item]['count']):
                    items.append({item: i})
            random.shuffle(items)
            for act in banc.info['Actors']:
                if act['Name'] in item_names:
                    new_item = items.pop()
                    name = list(new_item.keys())[0]
                    id = list(new_item.values())[0]
                    act['Gyaml'] = name
                    act['Name'] = name
                    if PARAMS['Collectables'][name]['needsID']:
                        act['spl__ItemWithPedestalBancParam'] = {'PlacementID': oead.S32(id)}
                    else:
                        act['spl__ItemWithPedestalBancParam'] = {}
                        if name == 'ItemIkuraBottle':
                            act['spl__ItemIkuraBottleBancParam'] = {
                                'DropIkuraValue': oead.S32(10),
                                'DropNum': oead.S32(10)
                            }

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


    def editWeaponChoices(self, mission_name: str, mission_data: zs_tools.BYAML, ui_missions_data: zs_tools.BYAML) -> None:
        if mission_name.split('_', 1)[1] not in LOGIC["Missions"]:
            return

        if len(mission_data.info['OctaSupplyWeaponInfoArray']) > 0:
            while len(mission_data.info['OctaSupplyWeaponInfoArray']) < 3:
                mission_data.info['OctaSupplyWeaponInfoArray'].append(
                    mission_data.info['OctaSupplyWeaponInfoArray'][-1])

        for i in range(len(mission_data.info['OctaSupplyWeaponInfoArray'])):
            e = mission_data.info['OctaSupplyWeaponInfoArray'][i]

            if i == 0: # leave first option as vanilla if it is a hero weapon
                try:
                    if e['SupplyWeaponType'] == 'Hero':
                        continue
                except KeyError:
                    continue

            weapon = self.weapon_placements[mission_name][i]

            if weapon.startswith("Sp") and not weapon.startswith("Spinner"):
                if '+' in weapon:
                    special_weapon, main_weapon = weapon.split('+')
                else:
                    special_weapon = weapon
                    main_weapon = "Free"
                e['SubWeapon'] = ""
                e['SpecialWeapon'] = f"Work/Gyml/{special_weapon}.spl__WeaponInfoSpecial.gyml"
                if weapon.startswith("SpSuperHook_Mission"):
                    e["SupplyWeaponType"] = "MainAndSpecial"
                    e['WeaponMain'] = f"Work/Gyml/{main_weapon}.spl__WeaponInfoMain.gyml"
                    if main_weapon == "Free":
                        e["WeaponMain"] = ""
                else:
                    e["SupplyWeaponType"] = "Special"
                continue

            e['SupplyWeaponType'] = "Normal"
            main_weapon, sub_weapon = weapon.split('+')
            e['WeaponMain'] = f"Work/Gyml/{main_weapon}.spl__WeaponInfoMain.gyml"
            e['SubWeapon'] = f"Work/Gyml/{sub_weapon}.spl__WeaponInfoSub.gyml"
            if main_weapon == "Free":
                e["WeaponMain"] = ""
            if sub_weapon == "Free":
                e["SubWeapon"] = ""

        for info in ui_missions_data.info:
            if 'MapNameLabel' in info:
                if info['MapNameLabel'] == mission_data.info['MapNameLabel']:
                    info['OctaSupplyWeaponInfoArray'] = mission_data.info['OctaSupplyWeaponInfoArray']


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


    def removeCutscenes(self, zs_data):
        """Most cutscenes we allow to be skipped through a DemoSkipTable. But some either don't work or give issues.

        Lots of levels contain the same data embedded in them, in which the first one loaded is cached.

        So we edit every instance of the rest of the cutscenes that we want to speed up or delete entirely"""

        unneeded_events = ['Mission_IntroduceComrade', 'Mission_BigWorldTutorial', 'Mission_IntroduceTrinity']
        event_files = [str(f) for f in zs_data.reader.get_files() if f.name.endswith('.bfevfl')]
        for f in event_files:
            if any(s in f for s in unneeded_events):
                del zs_data.writer.files[f]
            if 'Mission_AppearSmallWorldBoss' in f:
                flow = event_tools.readFlow(zs_data.writer.files[f])
                zs_data.writer.files[f] =\
                    self.skipCutscene(flow, 'EntryPoint0', 'Event46')
            if 'Mission_TreasureMarge' in f:
                flow = event_tools.readFlow(zs_data.writer.files[f])
                zs_data.writer.files[f] =\
                    self.skipCutscene(flow, 'EntryPoint0', 'Event49')
            if 'Mission_DestroyLaunchPadKebaInk' in f:
                flow = event_tools.readFlow(zs_data.writer.files[f])
                zs_data.writer.files[f] =\
                    self.skipCutscene(flow, 'EntryPoint0', 'Event12')


    def updateMissionParameters(self):
        if not self.settings['Hero Gear Upgrades'] and not self.settings['Skip Cutscenes']:
            return

        singleton_files = [f.name for f in (self.rom_path / 'Pack').iterdir() if f.name.startswith('SingletonParam')]
        if not singleton_files:
            return

        for f in singleton_files: # if there is a SingletonParam_v700 or higher, use that
            param_file = f
        with open(self.rom_path / 'Pack' / param_file, 'rb') as f:
            zs_data = zs_tools.SARC(f.read())

        # So currently using the map only allows you to jump to kettles that happen to be in their original site
        # I thought this would fix that, but nope

        # if self.settings['Levels']:
        #     table_file = 'Gyml/Singleton/spl__MissionStageTable.spl__MissionStageTable.bgyml'
        #     stage_table = zs_tools.BYAML(zs_data.writer.files[table_file])
        #     for stage in stage_table.info['Rows']:
        #         if stage['StageName'].startswith('Msn_A'):
        #             loc = [i for i in self.levels if self.levels[i] == stage['StageName']][0]
        #             site_num = loc[6]
        #             nums = {'r': '2', 'a': '4', 'n': '6', 'S': '1'}
        #             if site_num in nums:
        #                 site_num = nums[site_num]
        #             stage['WorldAreaType'] = 'BigWorld' + site_num
        #     zs_data.writer.files[table_file] = stage_table.repack()

        if self.settings['Hero Gear Upgrades']:
            skills = [s for s in PARAMS['Upgrade_Skills']]
            random.shuffle(skills)
            skill_file = 'Gyml/Singleton/spl__MissionConstant.spl__MissionConstant.bgyml'
            skill_table = zs_tools.BYAML(zs_data.writer.files[skill_file])
            for skill in skill_table.info['PlayerSkillTree']['SkillIconTable']:
                new_skill = random.choice(skills)
                skills.remove(new_skill)
                skill['SkillType'] = new_skill
                if new_skill == 'HeroShotUp':
                    del skill['SkillType']
            zs_data.writer.files[skill_file] = skill_table.repack()

        if self.settings['Skip Cutscenes']:
            skip_file = 'Gyml/Singleton/spl__MissionDemoSkipTable.spl__MissionDemoSkipTable.bgyml'
            skip_table = zs_tools.BYAML(zs_data.writer.files[skip_file])
            cuts = copy.deepcopy(PARAMS['Cutscenes'])
            for cutscene in skip_table.info['Rows']:
                name = cutscene['DemoName'].split('/')[3].split('.')[0]
                if name in cuts:
                    cutscene['DemoSkipCondition'] = 'Always'
                    cuts.remove(name)
            for cutscene in cuts:
                skip_table.info['Rows'].append({
                    'DemoName': f'Work/Event/EventSetting/{cutscene}.engine__event__EventSettingParam.gyml',
                    'DemoSkipCondition': 'Always'
                })
            zs_data.writer.files[skip_file] = skip_table.repack()

        with open(self.out_dir / 'Pack' / param_file, 'wb') as f:
            f.write(zs_data.repack())


    def randomizeEnemies(self, zs_data: zs_tools.SARC) -> None:
        banc_file = [str(f) for f in zs_data.reader.get_files() if f.name.endswith('.bcett.byml')][0]
        banc = zs_tools.BYAML(zs_data.writer.files[banc_file])
        for act in banc.info['Actors']:
            if not self.thread_active:
                break
            if act['Name'] in PARAMS['Enemies']:
                if self.settings['Enemies']:
                    enemy = random.choice(PARAMS['Enemies'])
                    while 'Shield' in enemy: # 1/5 enemies will be shielded so lets trim that down
                        if random.randint(1, 2) == 2:
                            break
                        enemy = random.choice(PARAMS['Enemies'])
                    act['Name'] = enemy
                    act['Gyaml'] = enemy
                size = 1.0
                if self.settings['Enemy Sizes']:
                    size = random.uniform(0.5, 2.0)
                    act['Scale'] = oead.byml.Array([oead.F32(size) for s in range(3)])
                if enemy.endswith('Takopter'):
                    act['Translate'][1] = oead.F32(float(act['Translate'][1]) + (1.5 * size))
        zs_data.writer.files[banc_file] = banc.repack()


    def randomizeText(self) -> None:
        if not self.settings['Text']:
            return

        self.status_update.emit("Randomizing text...")

        message_files = [f.name for f in (self.rom_path / 'Mals').iterdir()]
        for file in message_files:
            if not self.thread_active:
                break
            with open(self.rom_path / 'Mals' / file, 'rb') as f:
                zs_data = zs_tools.SARC(f.read())

            # get all files that we want to edit
            mission_text_files = [str(f) for f in zs_data.reader.get_files()
                                  if str(f).startswith(('LogicMsg/', 'CommonMsg/Mission/'))
                                  or str(f).split('/')[-1].startswith(('Mission_', 'Msn_'))]
            for text_file in reversed(mission_text_files):
                if 'AlternaLog' in text_file:
                    mission_text_files.remove(text_file)
                if 'MissionStageName' in text_file:
                    mission_text_files.remove(text_file)

            # store the messages in an array, shuffle it, then replace the old messages with the shuffled ones
            text_entries = []
            for text_file in mission_text_files:
                text_entries.extend(text_tools.getText(zs_data.writer.files[text_file]))
            random.shuffle(text_entries)
            for text_file in mission_text_files:
                zs_data.writer.files[text_file] = text_tools.randomizeText(zs_data.writer.files[text_file], text_entries)

            # finally, repack the sarc archive
            with open(self.out_dir / 'Mals' / file, 'wb') as f:
                f.write(zs_data.repack())


    # STOP THREAD
    def stop(self):
        self.thread_active = False
