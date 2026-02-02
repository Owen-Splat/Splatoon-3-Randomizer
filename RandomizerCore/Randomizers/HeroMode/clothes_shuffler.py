from RandomizerCore.Randomizers import common
import oead, time


# TODO: Clean up this code, it is very messy work right now lol
def randomizeClothes(thread) -> None:
    """Randomizes the hero clothes and armor into matching sets"""

    # Update the ui status and add a slight delay so that the user has time to read it
    thread.status_update.emit("Randomizing hero clothes...")
    time.sleep(1)

    # load gear datasheets
    file_name_head, head_info = common.loadRSDB(thread.rom_path, "GearInfoHead")
    file_name_clothes, clothes_info = common.loadRSDB(thread.rom_path, "GearInfoClothes")
    file_name_shoes, shoes_info = common.loadRSDB(thread.rom_path, "GearInfoShoes")

    # get a dict of key Id and value [head, clothes, shoes]
    gear_sets = {}
    hero_ids = set()
    for entry in head_info.info:
        gear_sets[int(entry["Id"])] = [entry["__RowId"]]
        if "_MSN" in entry["__RowId"]: # we only need one file to get all hero ids
            hero_ids.add(int(entry["Id"]))
    for entry in clothes_info.info:
        if int(entry["Id"]) in gear_sets:
            gear_sets[int(entry["Id"])].append(entry["__RowId"])
    for entry in shoes_info.info:
        if int(entry["Id"]) in gear_sets:
            gear_sets[int(entry["Id"])].append(entry["__RowId"])

    # change hero_ids to a list so that it is subscriptable
    hero_ids = list(hero_ids)

    # delete hero entries from our gear dict
    for id in hero_ids:
        del gear_sets[id]

    # delete gear entries if there are not 3 pieces in the set
    for k,v in gear_sets.copy().items():
        if len(v) < 3:
            del gear_sets[k]

    # delete hero entries from the datasheets
    for entry in reversed(head_info.info):
        if int(entry["Id"]) in hero_ids:
            del entry
    for entry in reversed(clothes_info.info):
        if int(entry["Id"]) in hero_ids:
            del entry
    for entry in reversed(shoes_info.info):
        if int(entry["Id"]) in hero_ids:
            del entry

    # now get x unique ids to change to the hero ids
    ids = thread.rng.sample(list(gear_sets.keys()), len(hero_ids))
    x = 0
    for entry in head_info.info:
        if int(entry["Id"]) in ids:
            entry["Id"] = oead.S32(hero_ids[x])
            x += 1
    x = 0
    for entry in clothes_info.info:
        if int(entry["Id"]) in ids:
            entry["Id"] = oead.S32(hero_ids[x])
            x += 1
    x = 0
    for entry in shoes_info.info:
        if int(entry["Id"]) in ids:
            entry["Id"] = oead.S32(hero_ids[x])
            x += 1

    # save gear datasheets
    common.saveRSDB(thread.out_dir, file_name_head, head_info)
    common.saveRSDB(thread.out_dir, file_name_clothes, clothes_info)
    common.saveRSDB(thread.out_dir, file_name_shoes, shoes_info)
