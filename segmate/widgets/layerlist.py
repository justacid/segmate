from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


from segmate.widgets.layeritem import LayerItemWidget


class LayerListWidget(QGroupBox):

    opacity_changed = Signal(int, float)
    layer_activated = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active = 0
        self.setTitle("Layer")

        self._layers = QVBoxLayout(self)
        self._layers.setSpacing(8)
        self._layers.setContentsMargins(2, 6, 2, 2)
        self._index = 0

    @property
    def count(self):
        return self._layers.count()

    def clear(self):
        if self._layers.count() == 0:
            return
        item = self._layers.takeAt(0)
        while item:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            item = self._layers.takeAt(0)
        self._index = 0

    def highlight(self, idx):
        if self.count == 0:
            return
        for i in range(self.count):
            child = self._layers.itemAt(i).widget()
            if i == idx:
                child.is_active = True
                continue
            child.is_active = False

    def add(self, title):
        item = LayerItemWidget(self._index, f"{title}".title())
        item.opacity_changed.connect(lambda l, o: self.opacity_changed.emit(l, o))
        item.layer_clicked.connect(self._layer_clicked)
        self._layers.addWidget(item)
        if self._index == 0:
            self.highlight(0)
        self._index += 1

    def _layer_clicked(self, idx):
        self.highlight(idx)
        self.layer_activated.emit(idx)
