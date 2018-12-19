from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import *


class LayerItem(QFrame):

    opacity_changed = Signal(float)

    def __init__(self, text, opacity=1.0):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(1)

        vbox = QVBoxLayout(self)
        vbox.setSpacing(1)
        vbox.setContentsMargins(1, 1, 1, 1)

        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        hbox.setContentsMargins(5, 2, 5, 3)

        self.button = QToolButton(self)
        self.button.setCheckable(False)
        hbox.addWidget(self.button)

        svbox = QVBoxLayout()
        self.label = QLabel(self)
        self.label.setText(text)
        svbox.addWidget(self.label)

        slider = QSlider(self)
        slider.setMaximum(100)
        slider.setValue(int(opacity * 100))
        slider.setOrientation(Qt.Horizontal)
        slider.setTickPosition(QSlider.TicksAbove)
        slider.setTickInterval(20)
        slider.valueChanged.connect(
            lambda x: self.opacity_changed.emit(x / 100))

        svbox.addWidget(slider)
        hbox.addLayout(svbox)
        vbox.addLayout(hbox)