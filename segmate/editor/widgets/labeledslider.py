from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class LabeledSlider(QFrame):

    value_changed = Signal(int)

    def __init__(self, label, *, value=0, minimum=1, maximum=20):
        super().__init__()

        layout = QVBoxLayout(self)

        label = QLabel(label)
        slider_layout = QHBoxLayout()
        slider = QSlider(Qt.Horizontal)
        slider.setValue(value)
        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        value_edit = QLineEdit(f"{value}")
        value_edit.setValidator(QIntValidator())
        value_edit.setAlignment(Qt.AlignCenter)
        value_edit.setFixedWidth(40)

        def edit_finished():
            val = int(value_edit.text())
            if val < minimum:
                val = minimum
            if val > maximum:
                val = maximum
            slider.setValue(val)
            value_edit.setText(f"{val}")
        value_edit.editingFinished.connect(edit_finished)

        def value_changed(value):
            value_edit.setText(f"{value}")
            self.value_changed.emit(value)
        slider.valueChanged.connect(value_changed)

        slider_layout.addWidget(slider)
        slider_layout.addWidget(value_edit)

        layout.addWidget(label)
        layout.addLayout(slider_layout)
