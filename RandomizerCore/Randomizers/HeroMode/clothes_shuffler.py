import oead, time

HERO_IDS = (27301, 27302, 27303, 27304, 27305) # 27306 hero gear replica? | 27310 captains clothes


def randomizeClothes(thread, matching: bool) -> None:
    """Randomizes the hero clothes and armor"""

    # load gear datasheets
    file_name_head, head_info = thread.parent().loadFile("RSDB", "GearInfoHead")
    file_name_clothes, clothes_info = thread.parent().loadFile("RSDB", "GearInfoClothes")
    file_name_shoes, shoes_info = thread.parent().loadFile("RSDB", "GearInfoShoes")

    # delete hero entries from the datasheets
    for entry in list(head_info.info):
        if int(entry["Id"]) in HERO_IDS:
            head_info.info.remove(entry)
    for entry in list(clothes_info.info):
        if int(entry["Id"]) in HERO_IDS:
            clothes_info.info.remove(entry)
    for entry in list(shoes_info.info):
        if int(entry["Id"]) in HERO_IDS:
            shoes_info.info.remove(entry)

    if matching:
        makeMatching(thread, head_info, clothes_info, shoes_info)
    else:
        makeRandom(thread, head_info, clothes_info, shoes_info)

    # save gear datasheets
    thread.parent().saveFile("RSDB", file_name_head, head_info)
    thread.parent().saveFile("RSDB", file_name_clothes, clothes_info)
    thread.parent().saveFile("RSDB", file_name_shoes, shoes_info)


def makeMatching(thread, head_info, clothes_info, shoes_info) -> None:
    """Only assigns random gear if there is a full match of 3 pieces"""

    # get a dict of key Id and value [head, clothes, shoes]
    gear_sets = {}
    for entry in head_info.info:
        gear_sets[int(entry["Id"])] = 1
    for entry in clothes_info.info:
        if int(entry["Id"]) in gear_sets:
            gear_sets[int(entry["Id"])] += 1
    for entry in shoes_info.info:
        if int(entry["Id"]) in gear_sets:
            gear_sets[int(entry["Id"])] += 1

    # delete gear entries if there are not 3 pieces in the set
    for k,v in gear_sets.copy().items():
        if v < 3:
            del gear_sets[k]

    # now get len(HERO_IDS) unique ids to change to the hero ids
    ids = thread.rng.sample(list(gear_sets.keys()), len(HERO_IDS))

    for i,id in enumerate(HERO_IDS):
        head_entry = [e for e in head_info.info if int(e["Id"]) == ids[i]][0]
        head_entry["Id"] = oead.S32(id)
        clothes_entry = [e for e in clothes_info.info if int(e["Id"]) == ids[i]][0]
        clothes_entry["Id"] = oead.S32(id)
        shoes_entry = [e for e in shoes_info.info if int(e["Id"]) == ids[i]][0]
        shoes_entry["Id"] = oead.S32(id)


def makeRandom(thread, head_info, clothes_info, shoes_info) -> None:
    """Assigns gear with no regard for matching or how it looks"""

    head_ids = [e["Id"] for e in head_info.info]
    head_ids = thread.rng.sample(head_ids, len(HERO_IDS))
    clothes_ids = [e["Id"] for e in clothes_info.info]
    clothes_ids = thread.rng.sample(clothes_ids, len(HERO_IDS))
    shoe_ids = [e["Id"] for e in shoes_info.info]
    shoe_ids = thread.rng.sample(shoe_ids, len(HERO_IDS))

    for i,id in enumerate(HERO_IDS):
        head_entry = [e for e in head_info.info if e["Id"] == head_ids[i]][0]
        head_entry["Id"] = oead.S32(id)
        clothes_entry = [e for e in clothes_info.info if e["Id"] == clothes_ids[i]][0]
        clothes_entry["Id"] = oead.S32(id)
        shoes_entry = [e for e in shoes_info.info if e["Id"] == shoe_ids[i]][0]
        shoes_entry["Id"] = oead.S32(id)
