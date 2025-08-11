from PySide6.QtCore import Qt, QEvent, QObject
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (QMainWindow, QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox,
                               QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget,
                               QSpacerItem, QSizePolicy, QApplication, QFileDialog)
from RandomizerUI.custom_widgets import *
from RandomizerCore.Data.randomizer_data import VERSION, CHANGES


class Ui_MainWindow(QObject):
    def setupUi(self, window: QMainWindow) -> None:
        window.setWindowTitle(f"Splatoon 3 Randomizer v{VERSION}")
        self.window = window
        self.spacing = 175

        central_widget = QWidget()
        vl = QVBoxLayout()

        label = QLabel("RomFS Path", central_widget)
        label.setFixedWidth(100)
        base_line = QLineEdit(central_widget)
        base_line.setObjectName("BaseLine")
        button = QPushButton("Browse", central_widget)
        button.clicked.connect(lambda: window.browseButtonClicked(base_line.objectName()))
        hl = QHBoxLayout()
        hl.addWidget(label)
        hl.addWidget(base_line)
        hl.addWidget(button)
        vl.addLayout(hl)

        # label = QLabel("DLC Path", central_widget)
        # label.setFixedWidth(100)
        # dlc_line = QLineEdit(central_widget)
        # dlc_line.setObjectName("DLCLine")
        # button = QPushButton("Browse", central_widget)
        # button.clicked.connect(lambda: window.browseButtonClicked(dlc_line.objectName()))
        # hl = QHBoxLayout()
        # hl.addWidget(label)
        # hl.addWidget(dlc_line)
        # hl.addWidget(button)
        # vl.addLayout(hl)

        label = QLabel("Output Path", central_widget)
        label.setFixedWidth(100)
        out_line = QLineEdit(central_widget)
        out_line.setObjectName("OutLine")
        button = QPushButton("Browse", central_widget)
        button.clicked.connect(lambda: window.browseButtonClicked(out_line.objectName()))
        hl = QHBoxLayout()
        hl.addWidget(label)
        hl.addWidget(out_line)
        hl.addWidget(button)
        vl.addLayout(hl)

        label = QLabel("Optional Seed", central_widget)
        label.setFixedWidth(100)
        seed_line = QLineEdit(central_widget)
        seed_line.setObjectName("SeedLine")
        seed_line.setPlaceholderText("Leave blank for random seed")
        button = QPushButton("Generate", central_widget)
        button.clicked.connect(window.seedButtonClicked)
        hl = QHBoxLayout()
        hl.addWidget(label)
        hl.addWidget(seed_line)
        hl.addWidget(button)
        vl.addLayout(hl)

        tab_widget = QTabWidget(central_widget)
        tab_widget.setObjectName("ModeTab")
        tab_widget.addTab(self.createTabHM(), "Hero Mode")
        tab_widget.addTab(self.createTabSO(), "Side Order")
        vl.addWidget(tab_widget, 5)
        central_widget.setLayout(vl)
        window.setCentralWidget(central_widget)

        for c in tab_widget.findChildren(QCheckBox):
            c.setFixedWidth(self.spacing)

        label = QLabel(central_widget)
        label.setObjectName('ExplanationText')
        label.setText('Hover over an option to see what it does')
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        label.setStyleSheet('color: rgb(80, 80, 80);')
        label.setFixedHeight(40)
        vl.addWidget(label)

        hl = QHBoxLayout()
        hl2 = QHBoxLayout()
        vl2 = QVBoxLayout()
        hl3 = QHBoxLayout()
        label = QLabel("Game Version", central_widget)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        major_version = QSpinBox(parent=central_widget, minimum=1, maximum=10, value=10)
        major_version.setObjectName("MajorVersion")
        minor_version = QSpinBox(parent=central_widget, minimum=0, maximum=3, value=0)
        minor_version.setObjectName("MinorVersion")
        patch_version = QSpinBox(parent=central_widget, minimum=0, maximum=2, value=1)
        patch_version.setObjectName("PatchVersion")
        vl2.addWidget(label)
        hl3.addWidget(major_version)
        hl3.addWidget(minor_version)
        hl3.addWidget(patch_version)
        vl2.addLayout(hl3)
        hl2.addLayout(vl2)
        platform_selector = RandoComboBox(central_widget)
        platform_selector.setObjectName("PlatformBox")
        platform_selector.addItems((
            "Platform: Console",
            "Platform: Emulator"
        ))
        platform_selector.upwards = True
        platform_selector.setFixedWidth(self.spacing)
        label = QLabel("", central_widget)
        label.setFixedWidth(30)
        hl2.addWidget(label)
        hl2.addWidget(platform_selector)
        hl.addLayout(hl2)
        hl.addSpacerItem(self.createHorizontalSpacer())
        button = QPushButton("RANDOMIZE", central_widget)
        button.setFixedWidth((button.width() * 3) // 2) # floored multiple of 1.5
        button.clicked.connect(window.randomizeButtonClicked)
        hl.addWidget(button)
        vl.addLayout(hl)

        window.show()

        # move to center after calling show()
        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = window.frameGeometry()
        geo.moveCenter(center)
        window.move(geo.topLeft())


    def createTabHM(self) -> QWidget:
        tab = QWidget()
        tab.setObjectName("HeroModeTab")
        vl = QVBoxLayout()

        # define all settings widgets first so that we can rearrange them easily later
        weapons_check = QCheckBox("Weapons", tab)
        weapons_check.setWhatsThis("Randomizes the weapons that each level can give.\nEach level will give 3 choices, with the first staying vanilla.")
        levels_check = QCheckBox("Levels", tab)
        levels_check.setWhatsThis("Randomizes which levels the kettles take you to.\nAfter Alterna is vanilla. One boss max per site.")
        cutscenes_check = QCheckBox("Skip Cutscenes", tab)
        cutscenes_check.setWhatsThis("Adds the skip button to most story cutscenes.\nSome cutscenes will automatically be skipped after 1 frame.")
        backgrounds_check = QCheckBox("Backgrounds", tab)
        backgrounds_check.setWhatsThis("Randomizes the background in every level and hub world.\nSometimes the background elements can block view of important stage elements.")
        color_check = QCheckBox("Ink Colors", tab)
        color_check.setWhatsThis("Randomizes the ink color in every level and hub world.")
        music_check = QCheckBox("Music", tab)
        music_check.setWhatsThis("Randomizes the music in every level and hub world.")
        upgrades_check = QCheckBox("Hero Gear Upgrades", tab)
        upgrades_check.setWhatsThis("Randomizes the placement of upgrades in the skill tree.")
        fuzzy_check = QCheckBox("Fuzzy Ooze Costs", tab)
        fuzzy_check.setWhatsThis("Randomizes the price of each fuzzy ooze.\nThese contain only vanilla prices, just shuffled around.")
        collectable_check = QCheckBox("Collectables", tab)
        collectable_check.setWhatsThis("Randomizes the location of each hidden collectable.\n25 egg cans are left vanilla.")
        enemy_check = QCheckBox("Enemies", tab)
        enemy_check.setWhatsThis("Randomizes every non-boss enemy.")
        sizes_check = QCheckBox("Enemy Sizes", tab)
        sizes_check.setWhatsThis("Randomizes the size of every non-boss enemy.")
        ohko_check = QCheckBox("Enemy Ink Is Lava", tab)
        ohko_check.setWhatsThis('Adds the "Enemy Ink Is Lava" challenge to every Alterna level.\nHaving armor will negate the challenge.')

        # now group the settings widgets together
        hl = QHBoxLayout()
        hl.addWidget(weapons_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(levels_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(cutscenes_check)
        vl.addLayout(hl)
        vl.addSpacerItem(self.createVerticalSpacer())
        hl = QHBoxLayout()
        hl.addWidget(backgrounds_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(color_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(music_check)
        vl.addLayout(hl)
        vl.addSpacerItem(self.createVerticalSpacer())
        hl = QHBoxLayout()
        hl.addWidget(upgrades_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(fuzzy_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(collectable_check)
        vl.addLayout(hl)
        vl.addSpacerItem(self.createVerticalSpacer())
        hl = QHBoxLayout()
        hl.addWidget(enemy_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(sizes_check)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(ohko_check)
        vl.addLayout(hl)

        tab.setLayout(vl)
        return tab


    def createTabSO(self) -> QWidget:
        tab = QWidget()
        tab.setObjectName("SideOrderTab")
        vl = QVBoxLayout()

        label = QLabel("Nothing here yet :)", tab)
        big_font = label.font()
        big_font.setPointSize(20)
        label.setFont(big_font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(label)

        tab.setLayout(vl)
        return tab


    def createHorizontalSpacer(self) -> QSpacerItem:
        return QSpacerItem(1, 30, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


    def createVerticalSpacer(self) -> QSpacerItem:
        return QSpacerItem(1, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)


    def setExplanationText(self, text: str = '') -> None:
        """Sets the text that explains what each option does"""

        if not text:
            text = "Hover over an option to see what it does"

        label = self.findLabel("ExplanationText")
        label.setText(text)

        if text.startswith("Hover"):
            label.setStyleSheet('color: rgb(80, 80, 80);')
        else:
            label.setStyleSheet('')


    def showChangelog(self) -> None:
        """Display new window listing the new features and bug fixes"""

        self.createMessageWindow("Changelog", CHANGES, with_scroll=True)


    def showUserError(self, msg) -> None:
        """Display new window to let the user know what went wrong - missing paths, bad logic, etc."""

        self.createMessageWindow("Error", msg)


    def createMessageWindow(self, title: str, text: str, with_scroll: bool = False) -> None:
        """Creates a new QMessageBox with the given window title and text

        This also matches the current Light/Dark Mode"""

        box = RandoHelpWindow(f"{self.window.windowTitle().split(" v")[0]} - {title}", text, with_scroll)
        box.exec()


    def openFileBrowser(self, dir: str) -> str:
        return QFileDialog.getExistingDirectory(self.window, 'Select Folder', dir)


    def findCheckBox(self, name: str) -> QCheckBox:
        check = self.window.findChild(QCheckBox, name)
        if check == None: # search by text if none were found
            for c in self.window.findChildren(QCheckBox):
                if c.text() == name:
                    check = c
                    break
        return check


    def findComboBox(self, name: str) -> RandoComboBox:
        return self.window.findChild(RandoComboBox, name)


    def findLabel(self, name: str) -> QLabel:
        return self.window.findChild(QLabel, name)


    def findLineEdit(self, name: str) -> QLineEdit:
        return self.window.findChild(QLineEdit, name)


    def findSpinBox(self, name: str) -> QSpinBox:
        return self.window.findChild(QSpinBox, name)


    def findTab(self, name: str) -> QWidget:
        return self.window.findChild(QWidget, name)


    def addOptionDescriptions(self) -> None:
        for widget in self.window.findChildren(QWidget):
            if widget.whatsThis() != "":
                widget.installEventFilter(self)


    def eventFilter(self, source: QWidget, event) -> bool:
        match event.type():
            case QEvent.Type.HoverEnter:
                self.setExplanationText(source.whatsThis())
            case QEvent.Type.HoverLeave:
                self.setExplanationText()

        return QWidget.eventFilter(self, source, event)



class Ui_ProgressWindow(QObject):
    def setupUi(self, title: str, window: QMainWindow) -> None:
        window.setWindowTitle(title)
        self.window = window

        central_widget = QWidget()
        vl = QVBoxLayout()

        self.label = QLabel("", central_widget)
        self.label.setMinimumWidth((len(title)*10)//1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_font = self.label.font()
        label_font.setPointSize(14)
        self.label.setFont(label_font)
        self.progress_bar = QProgressBar(central_widget)
        self.progress_bar.setMaximum(0) # non-progress bar, too lazy to calculate steps
        self.button = QPushButton("Test", central_widget)

        vl.addWidget(self.label)
        vl.addWidget(self.progress_bar)
        vl.addWidget(self.button)
        self.button.hide()

        central_widget.setLayout(vl)
        window.setCentralWidget(central_widget)
