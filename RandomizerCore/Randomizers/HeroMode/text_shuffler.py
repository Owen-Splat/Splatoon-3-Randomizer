from RandomizerCore.Tools import text_tools


# TODO: Could be cool to have an option to google translate the text
def randomizeText(thread) -> None:
    """Shuffles the labels to text relating to hero mode"""

    thread.status_update.emit("Randomizing text...")

    message_files = [f.name for f in (thread.parent().rom_path / "Mals").iterdir()]
    for file in message_files:
        if not thread.thread_active:
            break

        file, zs_data = thread.parent().loadFile("Mals", file)

        # get all files that we want to edit
        mission_text_files = [str(f) for f in zs_data.reader.get_files()
                                if str(f).startswith(("LogicMsg/", "CommonMsg/Mission/"))
                                or str(f).split('/')[-1].startswith(("Mission_", "Msn_"))]

        # TODO: Keep specific label:text entries vanilla instead of the whole file
        exclusions = (
            "Sdodr",
            "AlternaLog",
            "StageName",
            "StageInfo",
            "PointGuide",
            "Rogaining",
            "MainTV",
            "SelectWeapon",
            "Clear",
            "Menu"
        )

        for text_file in reversed(mission_text_files):
            if any(sub in text_file for sub in exclusions):
                mission_text_files.remove(text_file)

        # store the messages by length
        text_entries = [[], [], [], [], []]
        for text_file in mission_text_files:
            text_list = text_tools.getText(zs_data.writer.files[text_file])
            for entry in text_list:
                text_entries[text_tools.getTextLengthGroup(entry)].append(entry)

        # shuffle the text and replace old messages with the shuffled ones
        for group in text_entries:
            thread.cosmetic_rng.shuffle(group)
        for text_file in mission_text_files:
            zs_data.writer.files[text_file] =\
                text_tools.randomizeText(zs_data.writer.files[text_file], text_entries)

        # finally, repack the sarc archive
        thread.parent().saveFile("Mals", file, zs_data)
