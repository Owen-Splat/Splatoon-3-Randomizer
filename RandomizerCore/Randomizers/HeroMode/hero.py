from PySide6 import QtCore
from RandomizerCore.Randomizers.HeroMode import (background_shuffler,
collectable_shuffler, color_shuffler, cutscene_edits, enemy_shuffler,
level_shuffler, music_shuffler, ooze_shuffler, text_shuffler,
upgrade_shuffler, weapon_shuffler)
from RandomizerCore.Tools.zs_tools import BYAML, SARC
from pathlib import Path
import oead, random, time, traceback



class HeroMode_Process(QtCore.QThread):
    status_update = QtCore.Signal(str)
    error = QtCore.Signal(str)
    is_done = QtCore.Signal()


    def __init__(self, parent, settings: dict):
        QtCore.QThread.__init__(self, parent)
        self.rom_path = Path(settings["RomFS"])
        self.out_dir = Path(settings["Output"])
        self.rng = random.Random(settings["Seed"])
        self.settings = dict(settings["HeroMode"])
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
                self.levels = level_shuffler.randomizeLevels(self)

            # makes a dict of levels and weapon choices, each level is given 3 choices in increasing difficulty
            self.weapon_placements = {}
            if self.settings['Weapons']:
                self.weapon_placements = weapon_shuffler.randomizeWeapons(self)

            self.editLevels()
            self.updateMissionParameters()

            if self.settings["Text"]:
                text_shuffler.randomizeText(self)

        except Exception:
            er = traceback.format_exc()
            self.error.emit(er)

        finally:
            self.is_done.emit()


    # TODO: We will need this for randomizing Side Order as well to check valid weapons
    # There will probably be other general functions we will need as well
    # e.g. Streamlined Read/Write functions with automatic error handling
    # These functions/scripts will be in the root RandomizerCore/Randomizers folder
    def getGameVersion(self) -> str:
        """Get the version string from the RSDB folder in the RomFS

        In the case of the user having dumped multiple updates into the same directory, get the highest one"""

        rsdb_path = self.rom_path / "RSDB"
        markers = [int(f.stem.split('.')[2], 16) for f in rsdb_path.iterdir() if f.stem.startswith("ActorInfo")]
        version_string = hex(max(markers))[2:].lower()
        return version_string


    # iterate through all level files and randomize the level data
    def editLevels(self):
        """Iterates through all the level files and makes various changes based on settings"""

        self.status_update.emit('Editing Hero Mode levels...')
        time.sleep(1)

        ui_info_file = [f.name for f in (self.rom_path / 'RSDB').iterdir() if f.name.startswith('MissionMapInfo') and f.name.split('.')[2] == self.version][0]
        with open(self.rom_path / 'RSDB' / ui_info_file, 'rb') as f:
            ui_missions_data = BYAML(f.read(), compressed=True)

        missions = [f.name for f in (self.rom_path / 'Pack' / 'Scene').iterdir() if f.name.startswith('Msn_')
                    or f.name.split('.', 1)[0] in ('BigWorld', 'SmallWorld', 'LaunchPadWorld', 'LastBoss', 'LastBoss02')]
        for m in missions:
            if not self.thread_active:
                break

            msn = m.split('.', 1)[0]

            with open(self.rom_path / 'Pack' / 'Scene' / m, 'rb') as f:
                zs_data = SARC(f.read())

            if self.settings['Backgrounds']:
                background_shuffler.randomizeBackground(self.rng, msn, zs_data)

            if msn in ('BigWorld', 'SmallWorld'):
                self.editHubs(msn, zs_data)

            # mission info
            info_file = f'SceneComponent/MissionMapInfo/{msn}.spl__MissionMapInfo.bgyml'
            mission_data = BYAML(zs_data.writer.files[info_file])

            if self.settings['Levels']:
                level_shuffler.fixMissionCompatibility(self.levels, msn, mission_data)

            if self.settings['Ink Colors']:
                mission_data.info['TeamColor'] =\
                    f"Work/Gyml/{color_shuffler.getRandomColor(self.rng)}.game__gfx__parameter__TeamColorDataSet.gyml"

            if self.settings['Enemy Ink Is Lava'] and mission_data.info['MapType'].endswith('Stage'):
                self.addChallenges(mission_data)

            has_weapons = True if 'OctaSupplyWeaponInfoArray' in mission_data.info else False
            if has_weapons and self.settings['Weapons']:
                weapon_shuffler.editWeaponChoices(self, msn, mission_data, ui_missions_data)

            zs_data.writer.files[info_file] = mission_data.repack()

            # scene bgm
            if self.settings['Music']:
                music_shuffler.randomizeMusic(self.rng, msn, zs_data)

            if self.settings['Skip Cutscenes']:
                cutscene_edits.removeCutscenes(zs_data)

            if self.settings['Enemies'] or self.settings['Enemy Sizes']:
                enemy_shuffler.randomizeEnemies(self, zs_data)

            with open(self.out_dir / 'Pack' / 'Scene' / m, 'wb') as f:
                f.write(zs_data.repack())

        with open(self.out_dir / 'RSDB' / ui_info_file, 'wb') as f:
            f.write(ui_missions_data.repack())


    def editHubs(self, msn, zs_data: SARC):
        banc = BYAML(zs_data.writer.files[f'Banc/{msn}.bcett.byml'])

        if self.settings['Levels']:
            level_shuffler.changeKettleDestinations(banc, self.levels)

        if msn == 'BigWorld' and self.settings['Fuzzy Ooze Costs']:
            ooze_shuffler.shuffleCosts(self.rng, banc)

        if self.settings['Collectables']:
            collectable_shuffler.randomizeCollectables(self.rng, banc)

        zs_data.writer.files[f'Banc/{msn}.bcett.byml'] = banc.repack()


    # TODO: Eventually add random challenges (OHKO, Time Limit, etc)
    # Having reasonable time limits would require extra logic
    def addChallenges(self, mission_data: BYAML):
        """Adds the 'Enemy Ink Is Lava' challenge parameter to every level"""

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


    def updateMissionParameters(self):
        """Update parameters regarding upgrades and cutscenes"""

        if not self.settings['Hero Gear Upgrades'] and not self.settings['Skip Cutscenes']:
            return

        singleton_files = [f.name for f in (self.rom_path / 'Pack').iterdir() if f.name.startswith('SingletonParam')]
        if not singleton_files:
            return

        for f in singleton_files: # if there is a SingletonParam_v700 or higher, use that
            param_file = f
        with open(self.rom_path / 'Pack' / param_file, 'rb') as f:
            zs_data = SARC(f.read())

        # So currently using the map only allows you to jump to kettles that happen to be in their original site
        # I thought this would fix that, but nope

        # if self.settings['Levels']:
        #     table_file = 'Gyml/Singleton/spl__MissionStageTable.spl__MissionStageTable.bgyml'
        #     stage_table = BYAML(zs_data.writer.files[table_file])
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
            upgrade_shuffler.randomizeUpgrades(self.rng, zs_data)

        if self.settings['Skip Cutscenes']:
            cutscene_edits.addSkipButton(zs_data)

        with open(self.out_dir / 'Pack' / param_file, 'wb') as f:
            f.write(zs_data.repack())


    # STOP THREAD
    def stop(self):
        self.thread_active = False
