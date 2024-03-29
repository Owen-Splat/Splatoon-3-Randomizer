#!/usr/bin/env python3

from PySide6 import QtCore, QtGui, QtWidgets
import RandomizerUI.main_window as window
from RandomizerCore.Paths.randomizer_paths import RESOURCE_PATH, RUNNING_FROM_SOURCE
import os, sys

def interruptHandler(sig, frame):
    sys.exit(0)

# Allow keyboard interrupts
import signal
signal.signal(signal.SIGINT, interruptHandler)


# Set app id so the custom taskbar icon will show while running from source
if RUNNING_FROM_SOURCE:
    from ctypes import windll
    try:
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("Splatoon_3_Randomizer")
    except AttributeError:
        pass # Ignore for versions of Windows before Windows 7

build_icon = "icon.ico"
if sys.platform == "darwin": # mac
    build_icon = "icon.icns"

app = QtWidgets.QApplication([])
app.setStyle('fusion')
app.setWindowIcon(QtGui.QIcon(os.path.join(RESOURCE_PATH, build_icon)))

m = window.MainWindow()

# for keyboard interrupts
timer = QtCore.QTimer()
timer.start(100)
timer.timeout.connect(lambda: None)

sys.exit(app.exec())
