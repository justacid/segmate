from functools import partial

from PySide2.QtCore import *
from PySide2.QtWidgets import *

from ..editor import EditorScene
from .layerlist import LayerListWidget


class InspectorWidget(QWidget):

    image_changed = Signal()
    scene_changed = Signal(EditorScene)

    def __init__(self):
        super().__init__()
        self.scene = None
        self.current_image = 0
        self._slider_down_value = 0

        self._setup_ui()
        self.slider_box.hide()
        self.layer_box.hide()

    def set_scene(self, scene):
        self.scene = scene
        self.current_image = 0

        if not scene:
            self.slider_box.hide()
            self.layer_box.hide()
            self._remove_tool_inspector()
            return

        self._add_layer_widgets()
        self.slider.setValue(0)
        self.slider.setMaximum(self.scene.image_count-1)
        self.scene_changed.emit(scene)

        self.slider_box.show()
        self.layer_box.show()

    def show_next(self):
        if self.current_image < self.scene.image_count-1:
            command = ChangeImageCommand(
                self.slider, self.current_image, self.current_image + 1)
            command.setText("Next Image")
            self.scene.undo_stack.push(command)

    def show_previous(self):
        if self.current_image > 0:
            command = ChangeImageCommand(
                self.slider, self.current_image, self.current_image - 1)
            command.setText("Previous Image")
            self.scene.undo_stack.push(command)

    def change_image(self, idx):
        self.current_image = idx
        active_layer = self.scene.active_layer
        self.scene.load(idx)
        self.slider_box.setTitle(f"Image {idx+1}/{self.scene.image_count}")
        self._activate_layer(active_layer)
        self.image_changed.emit()

    def show_tool_inspector(self):
        self._remove_tool_inspector()
        self._add_tool_inspector()

    def _activate_layer(self, idx):
        self.scene.active_layer = idx
        self.scene.update()
        self.show_tool_inspector()

    def _slider_pressed(self):
        self._slider_down_value = self.slider.value()

    def _slider_released(self):
        command = ChangeImageCommand(
            self.slider, self._slider_down_value, self.slider.value())
        command.setText("Change Image")
        self.scene.undo_stack.push(command)

    def _add_tool_inspector(self):
        idx = self.scene.active_layer
        widget = self.scene.layers.tool_widget
        if widget:
            if not self.scene.layers.tool.is_editable:
                widget.setDisabled(True)
            self.dock_layout.insertWidget(1, widget)

    def _remove_tool_inspector(self):
        if self.dock_layout.count() <= 3:
            return
        widget = self.dock_layout.itemAt(1).widget()
        if widget:
            widget.deleteLater()

    def _add_layer_widgets(self):
        self.layer_box.clear()
        for index, name in enumerate(self.scene.data_store.folders):
            self.layer_box.add(f"{name}".title())

    def _change_layer_opacity(self, idx, value):
        self.scene.set_layer_opacity(idx, value)

    def _setup_ui(self):
        self.dock_layout = QVBoxLayout(self)
        self.dock_layout.setContentsMargins(4, 4, 4, 0)

        self.slider_box = QGroupBox("Images")
        self.slider_box.setObjectName("imageSlider")
        hlayout = QHBoxLayout(self.slider_box)

        arrow_left = QToolButton(self)
        arrow_left.setMaximumSize(25, 25)
        arrow_left.setArrowType(Qt.LeftArrow)
        left_action = QAction()
        left_action.triggered.connect(self.show_previous)
        arrow_left.setDefaultAction(left_action)
        hlayout.addWidget(arrow_left)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.change_image)
        self.slider.sliderPressed.connect(self._slider_pressed)
        self.slider.sliderReleased.connect(self._slider_released)
        hlayout.addWidget(self.slider)

        arrow_right = QToolButton()
        arrow_right.setMaximumSize(25, 25)
        arrow_right.setArrowType(Qt.RightArrow)
        right_action = QAction()
        right_action.triggered.connect(self.show_next)
        arrow_right.setDefaultAction(right_action)
        hlayout.addWidget(arrow_right)

        self.dock_layout.addWidget(self.slider_box)
        self.layer_box = LayerListWidget()
        self.layer_box.opacity_changed.connect(self._change_layer_opacity)
        self.layer_box.layer_activated.connect(self._activate_layer)
        self.dock_layout.addWidget(self.layer_box)
        self.dock_layout.addItem(
            QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))


class ChangeImageCommand(QUndoCommand):

    def __init__(self, slider, old_value, new_value):
        super().__init__()
        self.slider = slider
        self.old_value = old_value
        self.new_value = new_value

    def undo(self):
        if self.slider:
            self.slider.setValue(self.old_value)

    def redo(self):
        if self.slider:
            self.slider.setValue(self.new_value)
