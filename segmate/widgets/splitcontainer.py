from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class SplitContainer(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._panes = []
        self._splitter = QSplitter()
        self._splitter.setContentsMargins(0, 0, 0, 0)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._splitter)

    def add_pane(self, widget, *, width=0.3):
        assert 0.0 <= width <= 1.0, "Pane width must be in [0, 1]!"

        if widget is None:
            return
        if self._splitter.indexOf(widget) >= 0:
            return

        self._panes.append((widget, width))
        self._splitter.addWidget(widget)

        if len(self._panes) > 1:
            for i in range(1, len(self._panes)):
                self._panes[i][0].hide()

        parent_width = self.parent().width()
        self._splitter.setSizes([parent_width * w for _, w in self._panes])
