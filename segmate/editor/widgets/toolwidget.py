from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class EditorToolWidget(QWidget):

    def __init__(self, title):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        box = QGroupBox(title, self)
        self._box_layout = QVBoxLayout(box)
        layout.addWidget(box)

    def add_widget(self, widget):
        self._box_layout.addWidget(widget)

    def add_separator(self):
        self.add_widget(EditorSeparator())


class EditorSeparator(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
