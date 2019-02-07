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
        self.activate_layer(active_layer)
        self.image_changed.emit()

    def activate_layer(self, idx):
        self.scene.active_layer = idx
        self.show_tool_inspector()

        for i in range(self.layers.count()-1):
            child = self.layers.itemAt(i).widget()
            if i == idx:
                child.is_active = True
                continue
            child.is_active = False

    def show_tool_inspector(self):
        self._remove_tool_inspector()
        self._add_tool_inspector()

    def _slider_pressed(self):
        self._slider_down_value = self.slider.value()

    def _slider_released(self):
        command = ChangeImageCommand(
            self.slider, self._slider_down_value, self.slider.value())
        command.setText("Change Image")
        self.scene.undo_stack.push(command)

    def _add_tool_inspector(self):
        idx = self.scene.active_layer
        widget = self.scene.layers[idx]._tool.inspector_widget
        if widget:
            self.dock_layout.insertWidget(1, widget)

    def _remove_tool_inspector(self):
        if self.dock_layout.count() <= 2:
            return
        widget = self.dock_layout.itemAt(1).widget()
        if widget:
            widget.deleteLater()

    def _add_layer_widgets(self):
        if self.layers.count():
            item = self.layers.takeAt(0)
            while item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                item = self.layers.takeAt(0)

        for index, name in enumerate(self.scene.data_store.folders):
            item = LayerItemWidget(index, f"Opacity: {name}".title())
            item.opacity_changed.connect(self._change_layer_opacity)
            item.layer_clicked.connect(self.activate_layer)
            self.layers.addWidget(item)
        self.layers.addItem(QSpacerItem(1, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _change_layer_opacity(self, idx, value):
        self.scene.change_layer_opacity(idx, value)

    def _setup_ui(self):
        self.dock_layout = QVBoxLayout(self)

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

        self.layer_box = QGroupBox(self)
        self.layer_box.setTitle("Layer")
        self.layer_box.setStyleSheet("border-radius: 0px;")

        self.layers = QVBoxLayout(self.layer_box)
        self.layers.setSpacing(2)
        self.layers.setContentsMargins(2, 6, 2, 2)
        self.dock_layout.addWidget(self.layer_box)


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
