from RandomizerCore.Tools.zs_tools import BYAML, SARC
from randomizer_paths import DATA_PATH
import oead

with open(DATA_PATH / "HeroMode" / "backgrounds.txt", "r") as f:
    BACKGROUNDS = f.read().splitlines()


# TODO: Edit sun position, fog, and other parameters
def randomizeBackground(rng, msn: str, zs_data: SARC) -> None:
    """Randomly chooses a new Skysphere for the level"""

    if (msn[4] == 'C') or ("King" in msn) or ("Boss" in msn):
        return

    renders = [str(f) for f in zs_data.reader.get_files() if f.name.endswith("RenderingMission.bgyml")]
    if renders:
        render_data = BYAML(zs_data.writer.files[renders[0]])
        sky = rng.choice(BACKGROUNDS)
        render_data.info["Lighting"]["SkySphere"]["ActorName"] =\
            f"Work/Actor/{sky}.engine__actor__ActorParam.gyml"
        if "Crater" in sky:
            render_data.info["Lighting"]["SkySphere"]["Scale"] = oead.F32(5.0)
        zs_data.writer.files[renders[0]] = render_data.repack()
