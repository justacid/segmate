from functools import partial

from PySide2.QtCore import *
from PySide2.QtWidgets import *

from segmate.editor import EditorScene, EditorItem
from segmate.widgets.layeritem import LayerItemWidget


class InspectorWidget(QWidget):

    image_changed = Signal()
    scene_changed = Signal(EditorScene)

    def __init__(self):
        super().__init__()
        self.scene = None
        self.current_image = 0
        self._slider_active = False
        self._setup_ui()

    def set_scene(self, scene):
        self.scene = scene
        self.current_image = 0
        self.slider.setValue(0)
        self.slider.setMaximum(self.scene.image_count-1)
        self.scene.image_loaded.connect(self._add_layers)
        self.scene_changed.emit(scene)

    def show_next(self):
        if self.current_image < self.scene.image_count-1:
            self.slider.setValue(self.current_image + 1)

    def show_previous(self):
        if self.current_image > 0:
            self.slider.setValue(self.current_image - 1)

    def change_image(self, idx):
        self.current_image = idx
        active_layer = self.scene.active_layer
        self.scene.load(idx)
        self.slider_box.setTitle(f"Image {idx+1}/{self.scene.image_count}")
        self._highlight_layer(active_layer)
        self.image_changed.emit()

    def _clear_layers(self):
        while self.layers.count():
            child = self.layers.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _add_layers(self):
        if self._slider_active:
            return
        self._clear_layers()
        for i, (layer, name) in enumerate(zip(self.scene.layers, self.scene.loader.folders)):
            item = self._add_layer_widget(i, layer, name)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _add_layer_widget(self, idx, layer, name=""):
        opacity = self.scene.opacities[idx]
        text = f"Opacity: {name}".title()
        item = LayerItemWidget(text, opacity)
        item.opacity_changed.connect(lambda x: self.scene.change_layer_opacity(idx, x))
        item.layer_clicked.connect(lambda: self._highlight_layer(idx))
        self.layers.addWidget(item)
        return item

    def _highlight_layer(self, idx):
        self.scene.active_layer = idx
        for i in range(self.layers.count()-1):
            child = self.layers.itemAt(i).widget()
            if i == idx:
                child.is_active = True
                continue
            child.is_active = False

    def _enable_repaint(self, enabled):
        self._slider_active = not enabled

    def _setup_ui(self):
        dock_layout = QVBoxLayout(self)

        self.slider_box = QGroupBox("Images")
        self.slider_box.setStyleSheet("border-radius: 0px;")
        hlayout = QHBoxLayout(self.slider_box)

        arrow_left = QToolButton(self)
        arrow_left.setMaximumSize(25, 25)
        arrow_left.setArrowType(Qt.LeftArrow)
        left_action = QAction()
        left_action.triggered.connect(self.show_previous)
        arrow_left.setDefaultAction(left_action)
        hlayout.addWidget(arrow_left)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.change_image)
        self.slider.sliderPressed.connect(partial(self._enable_repaint, False))
        self.slider.sliderReleased.connect(partial(self._enable_repaint, True))
        hlayout.addWidget(self.slider)

        arrow_right = QToolButton()
        arrow_right.setMaximumSize(25, 25)
        arrow_right.setArrowType(Qt.RightArrow)
        right_action = QAction()
        right_action.triggered.connect(self.show_next)
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
