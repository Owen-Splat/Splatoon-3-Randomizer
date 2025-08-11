from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFrame, QLabel, QMainWindow,
                               QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget)


class RandoComboBox(QComboBox):
    """Custom QComboBox that overrides the showPopup() and hidePopup() methods"""

    def __init__(self, parent) -> None:
        super(RandoComboBox, self).__init__()
        self.setParent(parent)
        self.upwards: bool = False


    def showPopup(self) -> None:
        """Custom showPopup implementation to move it fully below or above the combobox"""

        QComboBox.showPopup(self)
        popup: QWidget = self.findChild(QFrame)
        pos_x = popup.x()
        pos_y = popup.y() + (self.height() * (self.currentIndex() + 1))
        if self.upwards:
            pos_y -= (self.height() + popup.height())
        popup.move(pos_x, pos_y)


    def hidePopup(self):
        """Custom hidePopup implementation to reset the explanation text"""

        QComboBox.hidePopup(self)
        if isinstance(self.window(), QMainWindow):
            self.window().ui.setExplanationText()



class RandoHelpWindow(QMessageBox):
    """Custom QMessageBox that supports scroll"""

    def __init__(self, title: str, text: str, with_scroll: bool = False):
        super(RandoHelpWindow, self).__init__()
        self.setWindowTitle(title)
        self.content = QWidget()
        vl = QVBoxLayout(self.content)
        if with_scroll:
            vl.addWidget(QLabel(text, self))
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setWidget(self.content)
            self.layout().addWidget(scroll, 0, 0, 1, 1)
            self.setStyleSheet("QScrollArea{min-width:600 px; min-height: 450px}")
        else:
            self.setText(text)
