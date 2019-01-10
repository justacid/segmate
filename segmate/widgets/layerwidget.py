from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class LayerWidget(QFrame):

    opacity_changed = Signal(float)
    layer_clicked = Signal()

    def __init__(self, text, opacity=1.0):
        super().__init__()

        self.opacity = opacity
        self.is_visible = True
        self.is_active = False
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        vbox = QVBoxLayout(self)
        vbox.setSpacing(1)
        vbox.setContentsMargins(1, 1, 1, 1)

        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        hbox.setContentsMargins(5, 2, 5, 3)

        self.button = QToolButton(self)
        self.action = QAction()
        self.setIcon(True)
        self.action.triggered.connect(self.toggleVisibility)
        self.button.setDefaultAction(self.action)
        hbox.addWidget(self.button)

        svbox = QVBoxLayout()
        self.label = QLabel(self)
        self.label.setText(text)
        self.label.setStyleSheet("border: 0;")
        svbox.addWidget(self.label)

        self.slider = QSlider(self)
        self.slider.setMaximum(100)
        self.slider.setValue(int(opacity * 100))
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.valueChanged.connect(self.changeOpacity)

        svbox.addWidget(self.slider)
        hbox.addLayout(svbox)
        vbox.addLayout(hbox)

    def setIcon(self, visible):
        if visible:
            self.action.setIcon(QIcon("icons/layer-visible.png"))
        else:
            self.action.setIcon(QIcon("icons/layer-invisible.png"))

    def mousePressEvent(self, event):
        self.is_active = not self.is_active
        self.setHighlight(self.is_active)
        self.layer_clicked.emit()
        event.ignore()

    def setHighlight(self, active):
        if active:
            self.setStyleSheet("QFrame { background-color: rgba(128, 0, 0, 255) }")
            return
        self.setStyleSheet("")

    def changeOpacity(self, value):
        self.is_visible = True
        self.opacity = value / 100

        if self.opacity == 0:
            self.is_visible = False

        self.setIcon(self.is_visible)
        self.opacity_changed.emit(self.opacity)

    def toggleVisibility(self):
        self.is_visible = not self.is_visible

        self.slider.blockSignals(True)
        value = 0
        if self.is_visible:
            value = 100 if self.opacity == 0 else int(self.opacity * 100)
        self.setIcon(self.is_visible)

        self.slider.setValue(value)
        self.opacity_changed.emit(value / 100)
        self.slider.blockSignals(False)
