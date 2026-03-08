from lms.message.msbtio import read_msbt as readMSBT
from lms.message.msbtio import write_msbt as writeMSBT


def getText(data) -> list:
    msbt = readMSBT(bytes(data))
    text_entries = [e.message.text for e in msbt.entries]
    return text_entries


def randomizeText(data, text_entries: list[list]) -> bytes:
    msbt = readMSBT(bytes(data))
    for entry in msbt.entries:
        try:
            entry.message.text = text_entries[getTextLengthGroup(entry.message.text)].pop(0)
        except:
            continue
    return writeMSBT(msbt)


def getTextLengthGroup(text: str) -> int:
    if len(text) <= 10:
        return 0
    if len(text) <= 25:
        return 1
    if len(text) <= 50:
        return 2
    if len(text) <= 75:
        return 3
    return 4
