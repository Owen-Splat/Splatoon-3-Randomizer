import oead, time

HERO_IDS = (27301, 27302, 27303, 27304, 27305) # 27306 hero gear replica? | 27310 captains clothes


def randomizeClothes(thread, matching: bool) -> None:
    """Randomizes the hero clothes and armor"""

    # load gear datasheets
    file_name_head, head_info = thread.parent().loadFile("RSDB", "GearInfoHead")
    file_name_clothes, clothes_info = thread.parent().loadFile("RSDB", "GearInfoClothes")
    file_name_shoes, shoes_info = thread.parent().loadFile("RSDB", "GearInfoShoes")

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
    ids = thread.cosmetic_rng.sample(list(gear_sets.keys()), len(HERO_IDS))

    for i,id in enumerate(HERO_IDS):
        hero_head = [e for e in head_info.info if int(e["Id"]) == id][0]
        new_head = [e for e in head_info.info if int(e["Id"]) == ids[i]][0]
        copyEntryInfo(new_head, hero_head)
        hero_clothes = [e for e in clothes_info.info if int(e["Id"]) == id][0]
        new_clothes = [e for e in clothes_info.info if int(e["Id"]) == ids[i]][0]
        copyEntryInfo(new_clothes, hero_clothes)
        hero_shoes = [e for e in shoes_info.info if int(e["Id"]) == id][0]
        new_shoes = [e for e in shoes_info.info if int(e["Id"]) == ids[i]][0]
        copyEntryInfo(new_shoes, hero_shoes)


def makeRandom(thread, head_info, clothes_info, shoes_info) -> None:
    """Assigns gear with no regard for matching or how it looks"""

    head_ids = [e["Id"] for e in head_info.info]
    head_ids = thread.cosmetic_rng.sample(head_ids, len(HERO_IDS))
    clothes_ids = [e["Id"] for e in clothes_info.info]
    clothes_ids = thread.cosmetic_rng.sample(clothes_ids, len(HERO_IDS))
    shoe_ids = [e["Id"] for e in shoes_info.info]
    shoe_ids = thread.cosmetic_rng.sample(shoe_ids, len(HERO_IDS))

    for i,id in enumerate(HERO_IDS):
        hero_head = [e for e in head_info.info if int(e["Id"]) == id][0]
        new_head = [e for e in head_info.info if e["Id"] == head_ids[i]][0]
        copyEntryInfo(new_head, hero_head)
        hero_clothes = [e for e in clothes_info.info if int(e["Id"]) == id][0]
        new_clothes = [e for e in clothes_info.info if e["Id"] == clothes_ids[i]][0]
        copyEntryInfo(new_clothes, hero_clothes)
        hero_shoes = [e for e in shoes_info.info if int(e["Id"]) == id][0]
        new_shoes = [e for e in shoes_info.info if e["Id"] == shoe_ids[i]][0]
        copyEntryInfo(new_shoes, hero_shoes)


def copyEntryInfo(info_entry, target_entry) -> None:
    """Copies the first entry's key:values to the target entry

    Excludes 'Id' and '__RowId' to keep the entries unique"""

    for k,v in info_entry.items():
        if k != "Id":
            target_entry[k] = v
