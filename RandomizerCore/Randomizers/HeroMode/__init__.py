from PySide6 import QtCore
import random, time, traceback

from . import background_shuffler
from . import clothes_shuffler
from . import collectable_shuffler
from . import color_shuffler
from . import cutscene_edits
from . import enemy_shuffler
from . import item_shuffler
from . import level_shuffler
from . import music_shuffler
from . import ooze_shuffler
from . import text_shuffler
from . import upgrade_shuffler
from . import weapon_shuffler


class HeroMode_Process(QtCore.QThread):
    """The thread for editing files relating to Hero Mode"""

    status_update = QtCore.Signal(str)
    error = QtCore.Signal(str)
    is_done = QtCore.Signal()


    def __init__(self, parent, seed: str, settings: dict) -> None:
        QtCore.QThread.__init__(self, parent)
        self.rng = random.Random(seed)
        self.settings = settings
        self.thread_active = True


    # automatically called when this thread is started
    def run(self):
        try:
            if self.settings['Levels'] and self.thread_active:
                self.levels = level_shuffler.randomizeLevels(self)

            if self.settings['Weapons'] and self.thread_active:
                self.hero_weapons = weapon_shuffler.randomizeHeroWeapons(self)
                self.weapon_placements = weapon_shuffler.randomizeWeapons(self, self.hero_weapons)
                self.ui_missions_info = {}

            if self.thread_active: self.editLevels()
            if self.thread_active: self.updateMissionParameters()
            if self.thread_active: self.editDatasheets()

            if self.settings["Text"] and self.thread_active:
                (self.parent().out_dir / 'Mals').mkdir(parents=True, exist_ok=True)
                text_shuffler.randomizeText(self)

        except Exception:
            er = traceback.format_exc()
            self.error.emit(er)

        finally:
            self.is_done.emit()


    def stop(self) -> None:
        """Overrides the QThread.stop() method to set the thread_active variable to False

        This variable is used to break loops when the user tries to close the window"""

        self.thread_active = False


    # iterate through all level files and randomize the level data
    def editLevels(self) -> None:
        """Iterates through all the level files and makes various changes based on settings"""

        self.status_update.emit('Editing Hero Mode levels...')
        time.sleep(1)

        (self.parent().out_dir / 'Pack' / 'Scene').mkdir(parents=True, exist_ok=True)

        missions = [f.name for f in (self.parent().rom_path / 'Pack' / 'Scene').iterdir()
                    if f.name.startswith('Msn_')
                    or f.name.split('.', 1)[0] in
                    ('BigWorld', 'SmallWorld', 'LaunchPadWorld', 'LastBoss', 'LastBoss02')]

        for m in missions:
            if not self.thread_active:
                break

            msn = m.split('.', 1)[0]

            m, level_sarc = self.parent().loadFile("Pack/Scene", m)

            if self.settings['Backgrounds']:
                background_shuffler.randomizeBackground(self.rng, msn, level_sarc)

            if msn in ('BigWorld', 'SmallWorld'):
                self.editHubs(msn, level_sarc)

            # mission info
            file_path = f"SceneComponent/MissionMapInfo/{msn}.spl__MissionMapInfo.bgyml"
            mission_data = self.parent().loadFromSarc(level_sarc, file_path)

            if self.settings['Levels']:
                level_shuffler.fixMissionCompatibility(self.levels, msn, mission_data)

            if self.settings['Ink Colors']:
                color = color_shuffler.getRandomColor(self.rng)
                mission_data.info['TeamColor'] =\
                    f"Work/Gyml/{color}.game__gfx__parameter__TeamColorDataSet.gyml"

            if self.settings['Enemy Ink Is Lava'] and mission_data.info['MapType'].endswith('Stage'):
                self.addChallenges(mission_data)

            has_weapons = True if 'OctaSupplyWeaponInfoArray' in mission_data.info else False
            if has_weapons and self.settings['Weapons']:
                weapon_shuffler.editWeaponChoices(self, msn, mission_data)

            self.parent().saveToSarc(level_sarc, file_path, mission_data)

            # scene bgm
            if self.settings['Music']:
                music_shuffler.randomizeMusic(self.rng, msn, level_sarc)

            if self.settings['Skip Cutscenes']:
                cutscene_edits.removeCutscenes(level_sarc)

            if self.settings['Enemies'] or self.settings['Enemy Sizes']:
                enemy_shuffler.randomizeEnemies(self, level_sarc)

            self.parent().saveFile("Pack/Scene", m, level_sarc)


    def editHubs(self, msn: str, hub_sarc) -> None:
        """Makes changes to the hub worlds

        This includes changing kettle destinations, ooze costs, and collectables"""

        file_path = f"Banc/{msn}.bcett.byml"
        banc = self.parent().loadFromSarc(hub_sarc, file_path)

        if self.settings['Levels']:
            level_shuffler.changeKettleDestinations(banc, self.levels)

        if msn == 'BigWorld' and self.settings['Fuzzy Ooze Costs']:
            ooze_shuffler.shuffleCosts(self.rng, banc)

        if self.settings['Collectables']:
            collectable_shuffler.randomizeCollectables(self.rng, banc)

        self.parent().saveToSarc(hub_sarc, file_path, banc)


    # TODO: Eventually add random challenges (OHKO, Time Limit, etc)
    # Having reasonable time limits would require extra logic
    def addChallenges(self, mission_data) -> None:
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


    def updateMissionParameters(self) -> None:
        """Update parameters regarding upgrades and cutscenes"""

        if not self.settings['Hero Gear Upgrades'] and not self.settings['Skip Cutscenes']:
            return

        if int(self.parent().version[0], 16) >= 7:
            file_name = "SingletonParam_v-700.pack.zs"
        else:
            file_name = "SingletonParam.pack.zs"

        file_name, param_sarc = self.parent().loadFile("Pack", file_name)

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
            upgrade_shuffler.randomizeUpgrades(self.rng, param_sarc)

        if self.settings['Skip Cutscenes']:
            cutscene_edits.addSkipButton(param_sarc)

        self.parent().saveFile("Pack", file_name, param_sarc)


    def editDatasheets(self) -> None:
        """Edits the datasheets in the RSDB folder"""

        if not self.settings["Weapons"] and not self.settings["Hero Clothes"]:
            return

        self.status_update.emit("Editing datasheets...")
        time.sleep(1)

        (self.parent().out_dir / 'RSDB').mkdir(parents=True, exist_ok=True)

        if self.settings["Weapons"]:
            weapon_shuffler.replaceHeroWeaponEntries(self.parent(), self.hero_weapons)
            weapon_shuffler.editLevelWeaponUI(self)

        if self.settings["Hero Clothes"] and self.thread_active:
            clothes_shuffler.randomizeClothes(self)
