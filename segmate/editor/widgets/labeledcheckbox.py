from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class LabeledCheckbox(QFrame):

    state_changed = Signal(bool)

    def __init__(self, label, *, callback=None, checked=False):
        super().__init__()

        layout = QHBoxLayout(self)

        label = QLabel(label)
        checkbox = QCheckBox()
        checkbox.setChecked(checked)

        def state_changed(value):
            self.state_changed.emit(value)

        checkbox.stateChanged.connect(state_changed)

        layout.addWidget(label)
        spacer = QSpacerItem(
            1, 1, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        layout.addWidget(checkbox)

        if callback is not None:
            self.state_changed.connect(callback)
