from functools import partial

from PySide2.QtCore import *
from PySide2.QtWidgets import *

from segmate.editor import EditorScene, EditorItem
from segmate.widgets.layerwidget import LayerWidget


class InspectorWidget(QWidget):

    image_changed = Signal()
    scene_changed = Signal(EditorScene)

    def __init__(self):
        super().__init__()
        self.scene = None
        self.current_image = 0
        self._slider_active = False
        self.setupUi()

    def setScene(self, scene):
        self.scene = scene
        self.current_image = 0
        self.slider.setValue(0)
        self.slider.setMaximum(self.scene.numImages()-1)
        self.scene.image_loaded.connect(self.addLayers)
        self.scene_changed.emit(scene)

    def showNextImage(self):
        if self.current_image < self.scene.numImages()-1:
            self.slider.setValue(self.current_image + 1)

    def showPreviousImage(self):
        if self.current_image > 0:
            self.slider.setValue(self.current_image - 1)

    def changeImage(self, idx):
        self.current_image = idx
        active_layer = self.scene.active_layer
        self.scene.load(idx)
        num_images = self.scene.numImages()
        self.slider_box.setTitle(f"Image {idx+1}/{num_images}")
        self.highlightLayer(active_layer)
        self.image_changed.emit()

    def clearLayers(self):
        while self.layers.count():
            child = self.layers.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addLayers(self):
        if self._slider_active:
            return
        self.clearLayers()
        for i, (layer, name) in enumerate(zip(self.scene.layers, self.scene.loader.folders)):
            item = self.addLayerWidget(i, layer, name)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def addLayerWidget(self, idx, layer, name=""):
        opacity = self.scene.getOpacity(idx)
        text = f"Opacity: {name}".title()
        item = LayerWidget(text, opacity)
        item.opacity_changed.connect(lambda x: self.scene.setOpacity(idx, x))
        item.layer_clicked.connect(lambda: self.highlightLayer(idx))
        self.layers.addWidget(item)
        return item

    def highlightLayer(self, idx):
        self.scene.setActive(idx)
        for i in range(self.layers.count()-1):
            child = self.layers.itemAt(i).widget()
            if i == idx:
                child.setHighlight(True)
                continue
            child.setHighlight(False)

    def _enable_repaint(self, enabled):
        self._slider_active = not enabled

    def setupUi(self):
        dock_layout = QVBoxLayout(self)

        self.slider_box = QGroupBox("Images")
        self.slider_box.setStyleSheet("border-radius: 0px;")
        hlayout = QHBoxLayout(self.slider_box)

        arrow_left = QToolButton(self)
        arrow_left.setMaximumSize(25, 25)
        arrow_left.setArrowType(Qt.LeftArrow)
        left_action = QAction()
        left_action.triggered.connect(self.showPreviousImage)
        arrow_left.setDefaultAction(left_action)
        hlayout.addWidget(arrow_left)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.changeImage)
        self.slider.sliderPressed.connect(partial(self._enable_repaint, False))
        self.slider.sliderReleased.connect(partial(self._enable_repaint, True))
        hlayout.addWidget(self.slider)

        arrow_right = QToolButton()
        arrow_right.setMaximumSize(25, 25)
        arrow_right.setArrowType(Qt.RightArrow)
        right_action = QAction()
        right_action.triggered.connect(self.showNextImage)
        arrow_right.setDefaultAction(right_action)
        hlayout.addWidget(arrow_right)

        dock_layout.addWidget(self.slider_box)

        layer_group = QGroupBox(self)
        layer_group.setTitle("Layer")
        layer_group.setStyleSheet("border-radius: 0px;")

        self.layers = QVBoxLayout(layer_group)
        self.layers.setSpacing(2)
        self.layers.setContentsMargins(2, 6, 2, 2)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        dock_layout.addWidget(layer_group)
