from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class LayerItemWidget(QFrame):

    opacity_changed = Signal(int, float)
    layer_clicked = Signal(int)

    def __init__(self, index, text):
        super().__init__()
        self._index = index
        self._text = text
        self._opacity = 1.0
        self._is_visible = True
        self._is_active = False
        self._setup_ui()
        qApp.installEventFilter(self)

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.slider.blockSignals(True)
        self.slider.setValue(int(value * 100))
        self.slider.blockSignals(False)

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
            self.setProperty("active", True)
            self.style().unpolish(self)
            self.style().polish(self)
            return
        self.setProperty("active", False)
        self.style().unpolish(self)
        self.style().polish(self)

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
        self.opacity_changed.emit(self._index, self.opacity)

    def _toggle_visibility(self):
        self._is_visible = not self._is_visible

        self.slider.blockSignals(True)
        value = 0
        if self._is_visible:
            value = 100 if self.opacity == 0 else int(self.opacity * 100)
        self._set_icon(self._is_visible)

        self.slider.setValue(value)
        self.opacity_changed.emit(self._index, value / 100)
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
        self.layer_clicked.emit(self._index)
        event.ignore()

    def eventFilter(self, object, event):
        # Do not intercept key events when a dialog is open
        if QApplication.activeModalWidget() is not None:
            return False

        if not hasattr(object, "type"):
            return False

        if event.type() == QEvent.KeyPress:
            if self.is_active and event.key() == Qt.Key_V:
                self._toggle_visibility()
                return True

        return False
