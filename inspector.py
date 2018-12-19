from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import *

from store import ImageScene
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
    scene_changed = Signal(ImageScene)

    def __init__(self):
        super().__init__()
        self.scene = None
        self.setupUi()

    def setScene(self, scene):
        self.scene = scene
        self.slider.setValue(0)
        self.slider.setMaximum(self.scene.numImages()-1)
        self.scene.image_loaded.connect(self.addLayers)
        self.scene_changed.emit(scene)

    def changeImage(self, idx):
        self.scene.load(idx)
        self.image_changed.emit(idx)

    def clearLayers(self):
        while self.layers.count():
            child = self.layers.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addLayers(self):

        def add(idx, layer):
            opacity = self.scene.opacities[idx]
            self.scene.setOpacity(idx, opacity)
            item = LayerItem(f"Opacity: Layer #{idx}", opacity)
            item.opacity_changed.connect(lambda x: self.scene.setOpacity(idx, x))
            self.layers.addWidget(item)

        self.clearLayers()
        for i, layer in enumerate(self.scene.layers):
            add(i, layer)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def setupUi(self):
        dock_layout = QVBoxLayout(self)

        slider_group = QGroupBox("Images")
        vlayout = QVBoxLayout(slider_group)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.changeImage)

        vlayout.addWidget(self.slider)
        dock_layout.addWidget(slider_group)

        layer_group = QGroupBox(self)
        layer_group.setTitle("Layers")
        self.layers = QVBoxLayout(layer_group)
        self.layers.setSpacing(2)
        self.layers.setContentsMargins(2, 2, 2, 2)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        dock_layout.addWidget(layer_group)
