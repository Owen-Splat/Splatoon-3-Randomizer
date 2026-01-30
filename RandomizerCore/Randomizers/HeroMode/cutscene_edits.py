from RandomizerCore.Tools.zs_tools import BYAML, SARC
from RandomizerCore.Tools import event_tools
from randomizer_paths import DATA_PATH
import random

with open(DATA_PATH / "HeroMode" / "cutscenes.txt", "r") as f:
    cutscene_list = f.read().splitlines()
CUTSCENES = [c for c in cutscene_list if not c.startswith('#')]


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


def skipCutscene(flow, before, after):
    event_tools.insertEventAfter(flow.flowchart, before, after)
    return event_tools.writeFlow(flow)


def removeCutscenes(zs_data: SARC):
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
                skipCutscene(flow, 'EntryPoint0', 'Event46')
        if 'Mission_TreasureMarge' in f:
            flow = event_tools.readFlow(zs_data.writer.files[f])
            zs_data.writer.files[f] =\
                skipCutscene(flow, 'EntryPoint0', 'Event49')
        if 'Mission_DestroyLaunchPadKebaInk' in f:
            flow = event_tools.readFlow(zs_data.writer.files[f])
            zs_data.writer.files[f] =\
                skipCutscene(flow, 'EntryPoint0', 'Event12')
