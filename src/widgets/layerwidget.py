from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class LayerWidget(QFrame):

    opacity_changed = Signal(float)

    def __init__(self, text, opacity=1.0):
        super().__init__()

        self.opacity = opacity
        self.is_visible = True

        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(1)

        vbox = QVBoxLayout(self)
        vbox.setSpacing(1)
        vbox.setContentsMargins(1, 1, 1, 1)

        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        hbox.setContentsMargins(5, 2, 5, 3)

        self.button = QToolButton(self)
        self.action = QAction()
        self.action.setIcon(QIcon("icons/visible.png"))
        self.action.triggered.connect(self.toggleVisibility)
        self.button.setDefaultAction(self.action)
        hbox.addWidget(self.button)

        svbox = QVBoxLayout()
        self.label = QLabel(self)
        self.label.setText(text)
        svbox.addWidget(self.label)

        self.slider = QSlider(self)
        self.slider.setMaximum(100)
        self.slider.setValue(int(opacity * 100))
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.valueChanged.connect(self.changeOpacity)

        svbox.addWidget(self.slider)
        hbox.addLayout(svbox)
        vbox.addLayout(hbox)

    def changeOpacity(self, value):
        self.is_visible = True
        self.opacity = value / 100

        if self.opacity == 0:
            self.is_visible = False
            self.action.setIcon(QIcon("icons/invisible.png"))
        else:
            self.action.setIcon(QIcon("icons/visible.png"))

        self.opacity_changed.emit(self.opacity)

    def toggleVisibility(self):
        self.is_visible = not self.is_visible

        self.slider.blockSignals(True)
        value = 0
        if self.is_visible:
            value = 100 if self.opacity == 0 else int(self.opacity * 100)
            self.action.setIcon(QIcon("icons/visible.png"))
        else:
            self.action.setIcon(QIcon("icons/invisible.png"))

        self.slider.setValue(value)
        self.opacity_changed.emit(value / 100)
        self.slider.blockSignals(False)
