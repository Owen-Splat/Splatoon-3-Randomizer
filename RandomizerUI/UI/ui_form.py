# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_form.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpinBox, QTabWidget, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(780, 440)
        MainWindow.setMinimumSize(QSize(780, 430))
        self.actionEnglish = QAction(MainWindow)
        self.actionEnglish.setObjectName(u"actionEnglish")
        self.actionfran_ais = QAction(MainWindow)
        self.actionfran_ais.setObjectName(u"actionfran_ais")
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.actionLight = QAction(MainWindow)
        self.actionLight.setObjectName(u"actionLight")
        self.actionDark = QAction(MainWindow)
        self.actionDark.setObjectName(u"actionDark")
        self.actionChangelog = QAction(MainWindow)
        self.actionChangelog.setObjectName(u"actionChangelog")
        self.actionPlanned_Features = QAction(MainWindow)
        self.actionPlanned_Features.setObjectName(u"actionPlanned_Features")
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.actionKnown_Issues = QAction(MainWindow)
        self.actionKnown_Issues.setObjectName(u"actionKnown_Issues")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 760, 331))
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(9)
        self.tabWidget.setFont(font)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tab.setAutoFillBackground(False)
        self.browseButton1 = QPushButton(self.tab)
        self.browseButton1.setObjectName(u"browseButton1")
        self.browseButton1.setGeometry(QRect(670, 5, 75, 23))
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.browseButton1.sizePolicy().hasHeightForWidth())
        self.browseButton1.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(9)
        font1.setBold(False)
        self.browseButton1.setFont(font1)
        self.browseButton1.setAutoFillBackground(False)
        self.browseButton1.setStyleSheet(u"background-color: rgb(218, 218, 218);")
        self.browseButton1.setFlat(False)
        self.lineEdit = QLineEdit(self.tab)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(100, 5, 561, 23))
        self.lineEdit.setFont(font1)
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 5, 81, 23))
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)
        self.label.setMinimumSize(QSize(75, 23))
        self.label.setFont(font1)
        self.label.setFrameShape(QFrame.NoFrame)
        self.label.setFrameShadow(QFrame.Plain)
        self.label.setTextFormat(Qt.PlainText)
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label.setWordWrap(False)
        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 65, 81, 23))
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)
        self.label_3.setMinimumSize(QSize(75, 23))
        self.label_3.setFont(font1)
        self.label_3.setFrameShape(QFrame.NoFrame)
        self.label_3.setFrameShadow(QFrame.Plain)
        self.label_3.setTextFormat(Qt.PlainText)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_3.setWordWrap(False)
        self.lineEdit_3 = QLineEdit(self.tab)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setGeometry(QRect(100, 65, 561, 23))
        self.lineEdit_3.setFont(font1)
        self.browseButton3 = QPushButton(self.tab)
        self.browseButton3.setObjectName(u"browseButton3")
        self.browseButton3.setGeometry(QRect(670, 65, 75, 23))
        sizePolicy1.setHeightForWidth(self.browseButton3.sizePolicy().hasHeightForWidth())
        self.browseButton3.setSizePolicy(sizePolicy1)
        self.browseButton3.setFont(font1)
        self.browseButton3.setAutoFillBackground(False)
        self.browseButton3.setStyleSheet(u"background-color: rgb(218, 218, 218);")
        self.browseButton3.setFlat(False)
        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 95, 81, 23))
        sizePolicy2.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy2)
        self.label_4.setMinimumSize(QSize(75, 23))
        self.label_4.setFont(font1)
        self.label_4.setFrameShape(QFrame.NoFrame)
        self.label_4.setFrameShadow(QFrame.Plain)
        self.label_4.setTextFormat(Qt.PlainText)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_4.setWordWrap(False)
        self.lineEdit_4 = QLineEdit(self.tab)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setGeometry(QRect(100, 95, 561, 23))
        self.lineEdit_4.setFont(font1)
        self.seedButton = QPushButton(self.tab)
        self.seedButton.setObjectName(u"seedButton")
        self.seedButton.setGeometry(QRect(670, 95, 75, 23))
        sizePolicy1.setHeightForWidth(self.seedButton.sizePolicy().hasHeightForWidth())
        self.seedButton.setSizePolicy(sizePolicy1)
        self.seedButton.setFont(font1)
        self.seedButton.setAutoFillBackground(False)
        self.seedButton.setStyleSheet(u"background-color: rgb(218, 218, 218);")
        self.seedButton.setFlat(False)
        self.tabWidget_2 = QTabWidget(self.tab)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tabWidget_2.setGeometry(QRect(10, 130, 731, 161))
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.kettleCheck = QCheckBox(self.tab_2)
        self.kettleCheck.setObjectName(u"kettleCheck")
        self.kettleCheck.setGeometry(QRect(20, 10, 151, 20))
        self.backgroundCheck = QCheckBox(self.tab_2)
        self.backgroundCheck.setObjectName(u"backgroundCheck")
        self.backgroundCheck.setGeometry(QRect(20, 55, 151, 20))
        self.gearCheck = QCheckBox(self.tab_2)
        self.gearCheck.setObjectName(u"gearCheck")
        self.gearCheck.setGeometry(QRect(20, 100, 151, 20))
        self.lavaCheck = QCheckBox(self.tab_2)
        self.lavaCheck.setObjectName(u"lavaCheck")
        self.lavaCheck.setGeometry(QRect(290, 10, 151, 20))
        self.inkCheck = QCheckBox(self.tab_2)
        self.inkCheck.setObjectName(u"inkCheck")
        self.inkCheck.setGeometry(QRect(290, 55, 151, 20))
        self.oozeCheck = QCheckBox(self.tab_2)
        self.oozeCheck.setObjectName(u"oozeCheck")
        self.oozeCheck.setEnabled(True)
        self.oozeCheck.setGeometry(QRect(290, 100, 151, 20))
        self.oozeCheck.setCheckable(True)
        self.cutsceneCheck = QCheckBox(self.tab_2)
        self.cutsceneCheck.setObjectName(u"cutsceneCheck")
        self.cutsceneCheck.setGeometry(QRect(560, 10, 151, 20))
        self.musicCheck = QCheckBox(self.tab_2)
        self.musicCheck.setObjectName(u"musicCheck")
        self.musicCheck.setGeometry(QRect(560, 55, 151, 20))
        self.collectCheck = QCheckBox(self.tab_2)
        self.collectCheck.setObjectName(u"collectCheck")
        self.collectCheck.setEnabled(True)
        self.collectCheck.setGeometry(QRect(560, 100, 151, 20))
        self.collectCheck.setCheckable(True)
        self.tabWidget_2.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tabWidget_2.addTab(self.tab_3, "")
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 35, 81, 23))
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        self.label_2.setMinimumSize(QSize(75, 23))
        self.label_2.setFont(font1)
        self.label_2.setFrameShape(QFrame.NoFrame)
        self.label_2.setFrameShadow(QFrame.Plain)
        self.label_2.setTextFormat(Qt.PlainText)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_2.setWordWrap(False)
        self.lineEdit_2 = QLineEdit(self.tab)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(100, 35, 561, 23))
        self.lineEdit_2.setFont(font1)
        self.browseButton2 = QPushButton(self.tab)
        self.browseButton2.setObjectName(u"browseButton2")
        self.browseButton2.setGeometry(QRect(670, 35, 75, 23))
        sizePolicy1.setHeightForWidth(self.browseButton2.sizePolicy().hasHeightForWidth())
        self.browseButton2.setSizePolicy(sizePolicy1)
        self.browseButton2.setFont(font1)
        self.browseButton2.setAutoFillBackground(False)
        self.browseButton2.setStyleSheet(u"background-color: rgb(218, 218, 218);")
        self.browseButton2.setFlat(False)
        self.tabWidget.addTab(self.tab, "")
        self.randomizeButton = QPushButton(self.centralwidget)
        self.randomizeButton.setObjectName(u"randomizeButton")
        self.randomizeButton.setGeometry(QRect(480, 390, 261, 41))
        font2 = QFont()
        font2.setPointSize(11)
        font2.setBold(False)
        self.randomizeButton.setFont(font2)
        self.randomizeButton.setAutoFillBackground(False)
        self.randomizeButton.setStyleSheet(u"background-color: rgb(218, 218, 218);")
        self.randomizeButton.setFlat(False)
        self.explainLabel = QLabel(self.centralwidget)
        self.explainLabel.setObjectName(u"explainLabel")
        self.explainLabel.setGeometry(QRect(20, 350, 731, 23))
        self.explainLabel.setStyleSheet(u"color: rgb(80, 80, 80);")
        self.seasonSpinBox = QSpinBox(self.centralwidget)
        self.seasonSpinBox.setObjectName(u"seasonSpinBox")
        self.seasonSpinBox.setGeometry(QRect(30, 390, 111, 41))
        font3 = QFont()
        font3.setPointSize(11)
        self.seasonSpinBox.setFont(font3)
        self.seasonSpinBox.setMinimum(1)
        self.seasonSpinBox.setMaximum(7)
        self.platformComboBox = QComboBox(self.centralwidget)
        self.platformComboBox.addItem("")
        self.platformComboBox.addItem("")
        self.platformComboBox.setObjectName(u"platformComboBox")
        self.platformComboBox.setGeometry(QRect(230, 390, 161, 41))
        self.platformComboBox.setFont(font3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.browseButton1.setDefault(False)
        self.browseButton3.setDefault(False)
        self.seedButton.setDefault(False)
        self.tabWidget_2.setCurrentIndex(0)
        self.browseButton2.setDefault(False)
        self.randomizeButton.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Splatoon 3 Randomizer", None))
        self.actionEnglish.setText(QCoreApplication.translate("MainWindow", u"English", None))
        self.actionfran_ais.setText(QCoreApplication.translate("MainWindow", u"Fran\u00e7ais", None))
        self.action.setText(QCoreApplication.translate("MainWindow", u"\u4e2d\u6587", None))
        self.actionLight.setText(QCoreApplication.translate("MainWindow", u"Light", None))
        self.actionDark.setText(QCoreApplication.translate("MainWindow", u"Dark", None))
        self.actionChangelog.setText(QCoreApplication.translate("MainWindow", u"What's New", None))
        self.actionPlanned_Features.setText(QCoreApplication.translate("MainWindow", u"Future", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.actionKnown_Issues.setText(QCoreApplication.translate("MainWindow", u"Known Issues", None))
        self.browseButton1.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.lineEdit.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"Base RomFS", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Output Folder", None))
        self.browseButton3.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Optional Seed", None))
        self.seedButton.setText(QCoreApplication.translate("MainWindow", u"New Seed", None))
#if QT_CONFIG(whatsthis)
        self.kettleCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Randomizes which levels the kettles take you to. Note that this weirdly affects superjumping", None))
#endif // QT_CONFIG(whatsthis)
        self.kettleCheck.setText(QCoreApplication.translate("MainWindow", u"Kettles", None))
#if QT_CONFIG(whatsthis)
        self.backgroundCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Randomizes the background in each level", None))
#endif // QT_CONFIG(whatsthis)
        self.backgroundCheck.setText(QCoreApplication.translate("MainWindow", u"Backgrounds", None))
#if QT_CONFIG(whatsthis)
        self.gearCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Randomizes the hero gear upgrades", None))
#endif // QT_CONFIG(whatsthis)
        self.gearCheck.setText(QCoreApplication.translate("MainWindow", u"Hero Gear Upgrades", None))
#if QT_CONFIG(whatsthis)
        self.lavaCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"This gives every Alterna level the additional challenge that you cannot touch enemy ink", None))
#endif // QT_CONFIG(whatsthis)
        self.lavaCheck.setText(QCoreApplication.translate("MainWindow", u"Enemy Ink Is Lava", None))
#if QT_CONFIG(whatsthis)
        self.inkCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Randomizes the ink color in every level, including the Crater, Alterna, and Rocket", None))
#endif // QT_CONFIG(whatsthis)
        self.inkCheck.setText(QCoreApplication.translate("MainWindow", u"Ink Color", None))
#if QT_CONFIG(whatsthis)
        self.oozeCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Randomizes the cost of fuzzy ooze in Alterna. Crater ooze is left vanilla", None))
#endif // QT_CONFIG(whatsthis)
        self.oozeCheck.setText(QCoreApplication.translate("MainWindow", u"Fuzzy Ooze Cost", None))
#if QT_CONFIG(whatsthis)
        self.cutsceneCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Adds a skip option to long cutscenes and dialogue", None))
#endif // QT_CONFIG(whatsthis)
        self.cutsceneCheck.setText(QCoreApplication.translate("MainWindow", u"Skip Cutscenes", None))
#if QT_CONFIG(whatsthis)
        self.musicCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Randomizes the music in every level", None))
#endif // QT_CONFIG(whatsthis)
        self.musicCheck.setText(QCoreApplication.translate("MainWindow", u"Music", None))
#if QT_CONFIG(whatsthis)
        self.collectCheck.setWhatsThis(QCoreApplication.translate("MainWindow", u"Randomizes the contents of the collectables", None))
#endif // QT_CONFIG(whatsthis)
        self.collectCheck.setText(QCoreApplication.translate("MainWindow", u"Collectables", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Return of the Mammalians", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Spire of Order", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"DLC RomFS", None))
        self.lineEdit_2.setText("")
        self.browseButton2.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Randomizer Settings", None))
        self.randomizeButton.setText(QCoreApplication.translate("MainWindow", u"Randomize", None))
        self.explainLabel.setText(QCoreApplication.translate("MainWindow", u"Hover over an option to see what it does", None))
        self.seasonSpinBox.setPrefix(QCoreApplication.translate("MainWindow", u" Season:  ", None))
        self.platformComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Platform: Console", None))
        self.platformComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Platform: Emulator", None))

    # retranslateUi

