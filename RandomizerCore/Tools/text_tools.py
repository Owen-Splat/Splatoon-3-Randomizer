from lms.message.msbtio import read_msbt as readMSBT
from lms.message.msbtio import write_msbt as writeMSBT
from io import BytesIO
import random


# def randomizeText(data) -> bytes:
#     msbt = readMSBT(bytes(data))

#     entry_names = []

#     for entry in msbt.entries:
#         entry_names.append(entry.name)

#     random.shuffle(entry_names)

#     for entry, name in zip(msbt.entries, entry_names):
#         entry.name = name

#     return writeMSBT(msbt)


def getText(data) -> list:
    msbt = readMSBT(bytes(data))
    text_entries = [e.message.text for e in msbt.entries]
    return text_entries


def randomizeText(data, text_entries: list) -> bytes:
    msbt = readMSBT(bytes(data))
    for entry in msbt.entries:
        try:
            entry.message.text = text_entries.pop(0)
        except:
            continue
    return writeMSBT(msbt)


# MESSAGE_PATH = Path(r"C:\Users\Owen3\Documents\LAS Extract\RomFS\regionUS\USen\message")
# p = MESSAGE_PATH.glob('**/*')
# files = [x.name for x in p if x.is_file() and x.name.endswith(".msbt")]
# for file in files:
#     with open(f"Test/output/{file}", 'wb') as f:
#         f.write(randomizeText(MESSAGE_PATH / file))
