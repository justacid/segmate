from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class LabeledSlider(QFrame):

    value_changed = Signal(int)

    def __init__(self, label, *, callback=None, value=0, minimum=1, maximum=20):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 3)

        label = QLabel(label)
        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider = QSlider(Qt.Horizontal)
        slider.setValue(value)
        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        value_edit = QLineEdit("{0}".format(value))
        value_edit.setValidator(QIntValidator())
        value_edit.setAlignment(Qt.AlignCenter)
        value_edit.setFixedWidth(30)

        def edit_finished():
            val = int(value_edit.text())
            if val < minimum:
                val = minimum
            if val > maximum:
                val = maximum
            slider.setValue(val)
            value_edit.setText("{0}".format(val))
        value_edit.editingFinished.connect(edit_finished)

        def value_changed(value):
            value_edit.setText("{0}".format(value))
            self.value_changed.emit(value)
        slider.valueChanged.connect(value_changed)

        slider_layout.addWidget(slider)
        slider_layout.addWidget(value_edit)

        layout.addWidget(label)
        layout.addLayout(slider_layout)

        if callback is not None:
            self.value_changed.connect(callback)
