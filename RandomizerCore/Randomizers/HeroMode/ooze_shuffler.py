from RandomizerCore.Tools.zs_tools import BYAML


def shuffleCosts(rng, banc: BYAML) -> None:
    """Randomizes the amount of power eggs to clear each fuzzy ooze"""

    # Instead of completely random prices, we want to shuffle the vanilla prices
    # So we need to iterate through the actor list twice
    ooze_costs = []
    for act in banc.info["Actors"]:
        if act["Name"].startswith("KebaInkCore"):
            ooze_costs.append(act['spl__KebaInkCoreBancParam']['NecessarySalmonRoe'])

    for act in banc.info['Actors']:
        if act['Name'].startswith('KebaInkCore'):
            act['spl__KebaInkCoreBancParam']['NecessarySalmonRoe'] =\
                ooze_costs[rng.randrange(len(ooze_costs))]
