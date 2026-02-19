from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QFrame, QLabel, QMainWindow, QMessageBox,
                               QScrollArea, QVBoxLayout, QWidget)


class RandoComboBox(QComboBox):
    """Custom QComboBox that overrides the showPopup() and hidePopup() methods"""

    def __init__(self, parent) -> None:
        super(RandoComboBox, self).__init__(parent)
        self.upwards: bool = False


    def showPopup(self) -> None:
        """Custom showPopup implementation to move it fully below or above the combobox
        
        This also prevents the popup from showing below or above the window.
        The contents of a window should stay within the bounds of the window"""

        QComboBox.showPopup(self)
        popup: QWidget = self.findChild(QFrame)

        # Because we went with the 'fusion' style, the currently selected item is in the position of the combobox
        # This means that the y position of the popup changes depending on the current index
        # We can use the current index and basic math to place the popup how we want it
        pos_y = popup.y() + (self.height() * (self.currentIndex() + 1))
        if self.upwards:
            pos_y -= (self.height() + popup.height())

        popup.move(popup.x(), pos_y)


    def hidePopup(self):
        """Custom hidePopup implementation to reset the explanation text
        
        Without this, the explanation text would continue to show the text for the combobox even after it has been closed"""

        QComboBox.hidePopup(self)
        if isinstance(self.window(), QMainWindow):
            self.window().ui.setExplanationText()



class RandoHelpWindow(QMessageBox):
    """Custom QMessageBox that supports scroll
    
    We also use stylesheets to control the minimum window size so that the text is always fully visible"""

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
            self.setStyleSheet("QScrollArea{min-width:600px; min-height: 450px}")
        else:
            self.setText(text)
            self.setStyleSheet("QLabel{min-width: 200px; min-height: 40px}")
