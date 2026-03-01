from RandomizerCore.Tools.zs_tools import BYAML, SARC
from RandomizerCore.Tools import event_tools
from randomizer_paths import DATA_PATH
import oead

with open(DATA_PATH / "HeroMode" / "cutscenes.txt", "r") as f:
    cutscene_list = f.read().splitlines()
CUTSCENES = [c for c in cutscene_list if not c.startswith('#')]

TRIGGERS = [
    16970736995762144716, # Mission_FirstKebaInk (avoidable cutscene before C-1)
    # 11962471988276804966, # Mission_BigWorldTutorial - this needs to play for a frame so that the player can use the menu
    12843054140135150154, # Mission_IntroduceTrinity
    14943589567981613895, # Mission_Area02First
    12555581493902236706, # Mission_Area03First
    6613581452132380588, # Mission_Area04First
    7291832044079309458, # Mission_Area04FirstB
    166864154025753383, # Mission_Area05First
    11252923247412202095, # Mission_Area05FirstB
    3117382206393141444, # Mission_Area06First
    16437576962706687477, # Mission_TrinityBecomeFriend
    1935498473693935787, # Mission_TrinityBecomeFriend (small 2nd trigger)
    12309113695328486721, # TESTING - Rocket intermission between R-1 and R-2 (not set up like the other triggers but positioned like it is)
]


def addSkipButton(zs_data: SARC) -> None:
    """Edits the MissionDemoSkipTable to give more cutscenes the skip button

    Unfortunately this does not work with every cutscene, and causes weird issues with others"""

    skip_file = 'Gyml/Singleton/spl__MissionDemoSkipTable.spl__MissionDemoSkipTable.bgyml'
    skip_table = BYAML(zs_data.writer.files[skip_file])
    cuts = CUTSCENES.copy()
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


def removeCutscenes(zs_data: SARC) -> None:
    """Most cutscenes we allow to be skipped through a DemoSkipTable. But some either don't work or give issues.

    Lots of levels contain the same data embedded in them, in which the first one loaded is cached.

    So we edit every instance of the rest of the cutscenes that we want to speed up or delete entirely"""

    unneeded_events = ['Mission_IntroduceComrade', 'Mission_BigWorldTutorial']#, 'Mission_IntroduceTrinity']
    event_files = [str(f) for f in zs_data.reader.get_files() if f.name.endswith('.bfevfl')]
    for f in event_files:
        if any(s in f for s in unneeded_events):
            del zs_data.writer.files[f]
        if 'Mission_AppearSmallWorldBoss' in f:
            flow = event_tools.readFlow(zs_data.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", "Event46")
            zs_data.writer.files[f] = event_tools.writeFlow(flow)
        if 'Mission_TreasureMarge' in f:
            flow = event_tools.readFlow(zs_data.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", "Event49")
            zs_data.writer.files[f] = event_tools.writeFlow(flow)
        if 'Mission_DestroyLaunchPadKebaInk' in f:
            flow = event_tools.readFlow(zs_data.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", "Event12")
            zs_data.writer.files[f] = event_tools.writeFlow(flow)


# TODO: Some events might not work without triggering for a frame
# An example is the first cutscene in Alterna where you meet the squid sisters
def removeCutsceneTriggers(banc: BYAML) -> None:
    """Removes the LocatorAreaSwitch actors that serve to trigger events"""

    for act in list(banc.info["Actors"]):
        if int(act["Hash"]) in TRIGGERS:
            banc.info["Actors"].remove(act)


def editTutorialCutscenes(tutorial_sarc: SARC) -> None:
    event_files = [str(f) for f in tutorial_sarc.reader.get_files() if f.name.endswith('.bfevfl')]
    for f in event_files:
        if "PlayerMake_WeaponGet" in f:
            flow = event_tools.readFlow(tutorial_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", "Event18")
            event_tools.insertEventAfter(flow.flowchart, "Event18", None)
            tutorial_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "PlayerMake_TrainArrival" in f:
            flow = event_tools.readFlow(tutorial_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", "Event6")
            tutorial_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "PlayerMake_ToPlaza" in f:
            flow = event_tools.readFlow(tutorial_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", "Event27")
            tutorial_sarc.writer.files[f] = event_tools.writeFlow(flow)


def editNewsCutscenes(news_sarc: SARC) -> None:
    event_files = [str(f) for f in news_sarc.reader.get_files() if f.name.endswith('.bfevfl')]
    for f in event_files:
        if "/Plaza_Overview." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint", "Event19")
            event_tools.insertEventAfter(flow.flowchart, "Event19", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/Plaza_Intro." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint", "Event15")
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/Plaza_IntroStation." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", "Event11")
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/News_Opening." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/News_Ending." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/News_FirstBoot." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/News_FirstBootSdodr." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/News_IntroFsodr." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/News_IntroSdodr." in f:
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
        if "/News_VersionUp." in f: # qol speed up
            flow = event_tools.readFlow(news_sarc.writer.files[f])
            event_tools.insertEventAfter(flow.flowchart, "EntryPoint0", None)
            news_sarc.writer.files[f] = event_tools.writeFlow(flow)
