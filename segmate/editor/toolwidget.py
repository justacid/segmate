from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class EditorToolWidget(QWidget):

    def __init__(self, title):
        super().__init__()

        inspector_layout = QVBoxLayout(self)
        inspector_layout.setContentsMargins(0, 0, 0, 0)
        box = QGroupBox(title, self)
        box.setStyleSheet("border-radius: 0px;")
        self._box_layout = QVBoxLayout(box)
        self._box_layout.setContentsMargins(2, 6, 2, 2)
        inspector_layout.addWidget(box)

    def add_widget(self, widget):
        self._box_layout.addWidget(widget)
