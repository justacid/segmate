from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import *

from layeritem import LayerItem


class InspectorDock(QDockWidget):

    def __init__(self, inspector):
        super().__init__("Inspector")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.setMinimumSize(250, 344)
        self.setWidget(inspector)


class Inspector(QWidget):

    image_changed = Signal(int)

    def __init__(self, scene=None):
        super().__init__()

        dock_layout = QVBoxLayout(self)
        self._setup_images_slider(dock_layout)
        self._add_layer_list(dock_layout)

        if scene:
            self.scene = scene
            num_images = len(self.scene.loader)
            self.slider.setMaximum(num_images)
            self.scene.changed.connect(self._set_layers)

    def set_scene(self, scene):
        self.scene = scene
        num_images = len(self.scene.loader)
        self.slider.setMaximum(num_images)
        self.scene.changed.connect(self._set_layers)

    def _setup_images_slider(self, dock_layout):
        group = QGroupBox("Images")
        vlayout = QVBoxLayout(group)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(lambda x: self.image_changed.emit(x))

        vlayout.addWidget(self.slider)
        dock_layout.addWidget(group)

    def _add_layer_list(self, dock_layout):
        group = QGroupBox(self)
        group.setTitle("Layers")
        self._layout = QVBoxLayout(group)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        dock_layout.addWidget(group)

    def _set_layers(self):
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for i, layer in enumerate(self.scene.layers):
            opacity = self.scene.opacities[i]
            item = LayerItem(f"Opacity: Layer #{i}", i, opacity=opacity)
            item.opacity_changed.connect(self.scene.set_opacity)
            self._layout.addWidget(item)
        self._layout.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

