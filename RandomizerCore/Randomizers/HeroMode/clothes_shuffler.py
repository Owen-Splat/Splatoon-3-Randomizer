import oead, time


# TODO: Clean up this code, it is very messy work right now lol
def randomizeClothes(thread) -> None:
    """Randomizes the hero clothes and armor into matching sets"""

    # load gear datasheets
    file_name_head, head_info = thread.parent().loadFile("RSDB", "GearInfoHead")
    file_name_clothes, clothes_info = thread.parent().loadFile("RSDB", "GearInfoClothes")
    file_name_shoes, shoes_info = thread.parent().loadFile("RSDB", "GearInfoShoes")

    hero_ids = [#27000, 27004, 27109, 27110, 27111, 27200,
                27301, 27302, 27303, 27304, 27305] # 27306 hero gear replica? | 27310 captains clothes
    hero_ids = [oead.S32(i) for i in hero_ids]

    # get a dict of key Id and value [head, clothes, shoes]
    gear_sets = {}
    for entry in head_info.info:
        gear_sets[int(entry["Id"])] = [entry["__RowId"]]
    for entry in clothes_info.info:
        if int(entry["Id"]) in gear_sets:
            gear_sets[int(entry["Id"])].append(entry["__RowId"])
    for entry in shoes_info.info:
        if int(entry["Id"]) in gear_sets:
            gear_sets[int(entry["Id"])].append(entry["__RowId"])

    # delete hero entries from our gear dict
    for id in hero_ids:
        del gear_sets[int(id)]

    # delete gear entries if there are not 3 pieces in the set
    for k,v in gear_sets.copy().items():
        if len(v) < 3:
            del gear_sets[k]

    # delete hero entries from the datasheets
    for entry in list(head_info.info):
        if entry["Id"] in hero_ids:
            head_info.info.remove(entry)
    for entry in list(clothes_info.info):
        if entry["Id"] in hero_ids:
            clothes_info.info.remove(entry)
    for entry in list(shoes_info.info):
        if entry["Id"] in hero_ids:
            shoes_info.info.remove(entry)

    # now get x unique ids to change to the hero ids
    ids = thread.rng.sample(list(gear_sets.keys()), len(hero_ids))

    for i,id in enumerate(hero_ids):
        head_entry = [e for e in head_info.info if int(e["Id"]) == ids[i]][0]
        head_entry["Id"] = id
        clothes_entry = [e for e in clothes_info.info if int(e["Id"]) == ids[i]][0]
        clothes_entry["Id"] = id
        shoes_entry = [e for e in shoes_info.info if int(e["Id"]) == ids[i]][0]
        shoes_entry["Id"] = id

    # save gear datasheets
    thread.parent().saveFile("RSDB", file_name_head, head_info)
    thread.parent().saveFile("RSDB", file_name_clothes, clothes_info)
    thread.parent().saveFile("RSDB", file_name_shoes, shoes_info)
