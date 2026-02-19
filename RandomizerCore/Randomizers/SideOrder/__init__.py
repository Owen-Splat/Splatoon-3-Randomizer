from PySide6 import QtCore
import random


class SideOrder_Process(QtCore.QThread):
    """The thread for editing files relating to Side Order"""

    status_update = QtCore.Signal(str)
    error = QtCore.Signal(str)
    is_done = QtCore.Signal()


    def __init__(self, parent, seed: str, settings: dict) -> None:
        QtCore.QThread.__init__(self, parent)
        self.rng = random.Random(seed)
        self.settings = settings
        self.thread_active = True
