from PySide2.QtCore import *
from PySide2.QtWidgets import *

from scene import ImageScene
from .layerwidget import LayerWidget


class InspectorWidget(QWidget):

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
        num_images = self.scene.numImages()
        self.slider_box.setTitle(f"Image {idx+1}/{num_images}")
        self.image_changed.emit(idx)

    def clearLayers(self):
        while self.layers.count():
            child = self.layers.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addLayers(self):

        def add(idx, layer, name):
            opacity = self.scene.getOpacity(idx)
            text = f"Opacity: {name}".title()
            item = LayerWidget(text, opacity)
            item.opacity_changed.connect(lambda x: self.scene.setOpacity(idx, x))
            self.layers.addWidget(item)

        self.clearLayers()
        for i, (layer, name) in enumerate(zip(self.scene.layers, self.scene.loader.folders)):
            add(i, layer, name)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def setupUi(self):
        dock_layout = QVBoxLayout(self)

        self.slider_box = QGroupBox("Images")
        vlayout = QVBoxLayout(self.slider_box)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.changeImage)

        vlayout.addWidget(self.slider)
        dock_layout.addWidget(self.slider_box)

        layer_group = QGroupBox(self)
        layer_group.setTitle("Layers")
        self.layers = QVBoxLayout(layer_group)
        self.layers.setSpacing(2)
        self.layers.setContentsMargins(2, 2, 2, 2)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        dock_layout.addWidget(layer_group)
