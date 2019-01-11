from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class LayerItemWidget(QFrame):

    opacity_changed = Signal(float)
    layer_clicked = Signal()

    def __init__(self, text, opacity=1.0):
        super().__init__()
        self._text = text
        self._opacity = opacity
        self._is_visible = True
        self._is_active = False
        self._setup_ui()

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, active):
        self._is_active = active
        if self._is_active:
            self.setStyleSheet("QFrame { background-color: rgba(128, 0, 0, 255) }")
            return
        self.setStyleSheet("")

    def _set_icon(self, visible):
        if visible:
            self._action.setIcon(QIcon("icons/layer-visible.png"))
        else:
            self._action.setIcon(QIcon("icons/layer-invisible.png"))

    def _change_opacity(self, value):
        self._is_visible = True
        self.opacity = value / 100

        if self.opacity == 0:
            self._is_visible = False

        self._set_icon(self._is_visible)
        self.opacity_changed.emit(self.opacity)

    def _toggle_visibility(self):
        self._is_visible = not self._is_visible

        self.slider.blockSignals(True)
        value = 0
        if self._is_visible:
            value = 100 if self.opacity == 0 else int(self.opacity * 100)
        self._set_icon(self._is_visible)

        self.slider.setValue(value)
        self.opacity_changed.emit(value / 100)
        self.slider.blockSignals(False)

    def _setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        vbox = QVBoxLayout(self)
        vbox.setSpacing(1)
        vbox.setContentsMargins(1, 1, 1, 1)

        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        hbox.setContentsMargins(5, 2, 5, 3)

        self._action = QAction()
        self._set_icon(True)
        self._action.triggered.connect(self._toggle_visibility)
        button = QToolButton(self)
        button.setDefaultAction(self._action)
        hbox.addWidget(button)

        svbox = QVBoxLayout()
        label = QLabel(self)
        label.setText(self._text)
        label.setStyleSheet("border: 0;")
        svbox.addWidget(label)

        self.slider = QSlider(self)
        self.slider.setMaximum(100)
        self.slider.setValue(int(self._opacity * 100))
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.valueChanged.connect(self._change_opacity)

        svbox.addWidget(self.slider)
        hbox.addLayout(svbox)
        vbox.addLayout(hbox)

    def mousePressEvent(self, event):
        self.is_active = not self.is_active
        self.layer_clicked.emit()
        event.ignore()