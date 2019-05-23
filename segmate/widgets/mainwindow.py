from functools import partial
from pathlib import Path

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import segmate
from segmate import settings
from segmate.widgets.inspector import InspectorWidget
from segmate.widgets.sceneview import SceneViewWidget
from segmate.store import DataStore
from segmate.editor import EditorScene, registry
from segmate.project import ProjectDialog, spf


class MainWindowWidget(QMainWindow):

    def __init__(self):
        super().__init__()
        self._project = None
        self._active_tool = "cursor_tool"
        self._recent_tool = None
        self._ask_before_closing = False

        self._setup_ui()
        self._add_menu()
        self._add_tool_bar()
        self._restore_window_position()
        self._load_last_opened()
        self._set_window_title()

    def _set_window_title(self, *, modified=False):
        title = f"Segmate {segmate.__version__} "
        project_name = ""
        if self._project is not None:
            project_name = f"- {self._project.archive_path}"
        modified_text = f" {'(*)' if modified else ''}"
        self.setWindowTitle(f"{title}{project_name}{modified_text}")

    def _restore_window_position(self):
        size, position, is_maximized = settings.window_position(self)
        if is_maximized:
            self.setWindowState(self.windowState() | Qt.WindowMaximized)
        self.resize(size)
        self.move(position)

    def _load_last_opened(self):
        last_opened = Path(settings.last_opened_project())
        if not last_opened.is_file() or ".spf" not in last_opened.suffix:
            return

        last_image_shown = settings.last_opened_image()
        self._project = spf.open_project(last_opened)
        self._open_project(self._project)
        self.inspector.slider.setValue(int(last_image_shown))
        self._set_window_title(modified=False)

    def _open_project(self, project):
        if project is None:
            return
        store = DataStore.from_project(project)
        self.inspector.set_scene(EditorScene(store))
        self.inspector.scene.image_modified.connect(self._mark_dirty)
        self.inspector.change_image(0)
        self.close_action.setEnabled(True)
        self._set_window_title()
        settings.set_last_opened_project(str(project.archive_path))
        settings.set_last_opened_image(0)

    def _close_project(self):
        if self._ask_before_closing:
            value = self._confirm_close_project()
            if value == QMessageBox.Cancel:
                return False
            elif value == QMessageBox.Save:
                self._save_to_disk()

        self._set_tool("cursor_tool")
        self.cursor_tool.setChecked(True)
        self._ask_before_closing = False

        if self.view.scene() is not None:
            del self.view.scene().data_store
        self.view.setScene(None)
        self.inspector.set_scene(None)
        self.close_action.setEnabled(False)
        settings.set_last_opened_project("")
        settings.set_last_opened_image(0)

        self._project = None
        self._set_window_title()
        return True

    def _open_project_dialog(self):
        if not self._close_project():
            return

        home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        filename = QFileDialog.getOpenFileName(
            self, "Open Project", home, "Segmate Project File (*.spf)")
        if filename[0]:
            self._project = spf.open_project(filename[0])
            self._open_project(self._project)
            self.close_action.setEnabled(True)

    def _new_project_dialog(self):
        if not self._close_project():
            return
        dialog = ProjectDialog(self)
        if dialog.exec() == QDialog.Rejected:
            return

        self._project = spf.new_project(dialog.project_path, dialog.data_root,
            dialog.folders, dialog.masks, dialog.editable, dialog.colors)
        self._ask_before_closing = False
        spf.save_project(self._project)
        self._open_project(self._project)

    def _confirm_close_project(self):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Warning!")
        msgbox.setText("You have unsaved changes.")
        msgbox.setInformativeText("Do you want to save or discard your changes?")
        msgbox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        msgbox.setIcon(QMessageBox.Warning)
        return msgbox.exec()

    def _save_to_disk(self):
        if self.inspector.scene:
            self.inspector.scene.save_to_disk()
            self._set_window_title()
            self.save_action.setEnabled(False)
            self._ask_before_closing = False
            if self._project is not None:
                spf.save_project(self._project)

    def _scene_changed(self, scene):
        self.view.setScene(scene)
        self._add_edit_menu(scene)

    def _set_tool(self, tool):
        if self._active_tool == tool:
            return
        self._recent_tool = self._active_tool
        self._active_tool = tool
        if self.view.scene() is None:
            return
        callback = lambda msg: self.statusBar().showMessage(msg, 2000)
        self.view.scene().layers.change_tool(tool, status_callback=callback)
        self.inspector.show_tool_inspector()
        self.view.scene().update()

    def _toggle_recent_tool(self):
        if self._recent_tool is None:
            return
        self._set_tool(self._recent_tool)

    def _mark_dirty(self):
        self._set_window_title(modified=True)
        self._ask_before_closing = True
        self.save_action.setEnabled(True)

    def _zoom_changed(self, zoom):
        self.zoom_submenu.setTitle(f"Zoom ({zoom}%)")
        try:
            idx = self.zoom_levels.index(zoom)
            self.zoom_group.actions()[idx].setChecked(True)
            self.zoom_group.actions()[-1].setText(f"Custom")
        except ValueError:
            self.zoom_group.actions()[-1].setChecked(True)
            self.zoom_group.actions()[-1].setText(f"Custom {zoom}%")

        message = f"Zoom: {zoom}%"
        self.statusBar().showMessage(message, 2000)

    def _zoom_to_fit_changed(self, toggled_on):
        if toggled_on:
            self.statusBar().showMessage("Zoom to fit: On")
            self.zoom_fit.setChecked(True)
        if not toggled_on:
            self.statusBar().showMessage("Zoom to fit: Off", 2000)
            self.zoom_fit.setChecked(False)

    def _arrow_keys_pressed(self, left_key):
        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        if left_key:
            self.inspector.show_previous()
        else:
            self.inspector.show_next()

    def _setup_ui(self):
        self.statusBar().showMessage("Ready")
        self.setWindowIcon(QIcon("icons/app-icon.png"))

        self.view = SceneViewWidget()
        self.view.setAlignment(Qt.AlignCenter)
        self.view.zoom_changed.connect(self._zoom_changed)
        self.view.fitview_changed.connect(self._zoom_to_fit_changed)
        self.setCentralWidget(self.view)

        self.inspector = InspectorWidget()
        self.inspector.scene_changed.connect(self._scene_changed)

        self.dock = QDockWidget("Inspector")
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock.setMinimumWidth(225)
        self.dock.setWidget(self.inspector)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        shortcut_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        shortcut_left.activated.connect(partial(self._arrow_keys_pressed, True))
        shortcut_right = QShortcut(QKeySequence(Qt.Key_Right), self)
        shortcut_right.activated.connect(partial(self._arrow_keys_pressed, False))
        shortcut_quicktoggle = QShortcut(QKeySequence(Qt.Key_Q), self)
        shortcut_quicktoggle.activated.connect(self._toggle_recent_tool)

    def _add_menu(self):
        self.new_project = QAction("&New Project")
        self.new_project.triggered.connect(self._new_project_dialog)
        self.new_project.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        self.open_action = QAction("&Open Project")
        self.open_action.setIcon(QIcon("icons/open-folder.png"))
        self.open_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.open_action.triggered.connect(self._open_project_dialog)
        self.close_action = QAction("&Close Project")
        self.close_action.triggered.connect(self._close_project)
        self.close_action.setEnabled(False)
        self.save_action = QAction("&Save Project")
        self.save_action.setIcon(QIcon("icons/save-current.png"))
        self.save_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        self.save_action.triggered.connect(self._save_to_disk)
        self.save_action.setEnabled(False)
        self.quit_action = QAction("&Quit")
        self.quit_action.triggered.connect(self.close)

        self.menuBar().setStyleSheet("QMenu::icon { padding: 5px; }")
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.new_project)
        file_menu.addAction(self.close_action)
        file_menu.addSeparator()
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.undo_action = QAction("Undo")
        self.undo_action.setEnabled(False)
        self.redo_action = QAction("Redo")
        self.redo_action.setEnabled(False)
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()

        self.fitview_action = QAction("Zoom to &Fit")
        self.fitview_action.setCheckable(True)
        self.fitview_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_F))
        self.fitview_action.triggered.connect(lambda: self.view.toggle_zoom_to_fit())

        view_menu = self.menuBar().addMenu("&View")
        inspector_action = self.dock.toggleViewAction()
        inspector_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_I))
        view_menu.addAction(self.dock.toggleViewAction())
        view_menu.addSeparator()
        view_menu.addAction(self.fitview_action)
        self.zoom_in = view_menu.addAction("Zoom &In")
        self.zoom_in.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Equal))
        self.zoom_in.triggered.connect(partial(self.view.zoom, 10))
        self.zoom_out = view_menu.addAction("Zoom &Out")
        self.zoom_out.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus))
        self.zoom_out.triggered.connect(partial(self.view.zoom, -10))
        view_menu.addSeparator()

        self.zoom_submenu = view_menu.addMenu("Zoom (100%)")
        self.zoom_group = QActionGroup(self.zoom_submenu)
        self.zoom_group.setExclusive(True)
        self.zoom_levels = list(range(20, 320, 20))

        for zoom in self.zoom_levels:
            action = self.zoom_group.addAction(f"{zoom}%")
            action.triggered.connect(partial(lambda z: self.view.set_zoom(z), zoom))
            action.setCheckable(True)
            if zoom == 100:
                action.setChecked(True)
            self.zoom_submenu.addAction(action)

        custom_zoom = self.zoom_group.addAction(f"Custom")
        custom_zoom.setCheckable(True)
        custom_zoom.setEnabled(False)
        self.zoom_submenu.addAction(custom_zoom)

        if registry.tools:
            self.plugin_menu = self.menuBar().addMenu("&Plugins")
            for name, tool in registry.tools.items():
                menu_entry, _ = tool
                if menu_entry is None:
                    menu_entry = name
                action = self.plugin_menu.addAction(menu_entry)
                action.triggered.connect(partial(self._set_tool, name))

    def _add_tool_bar(self):
        toolbar = super().addToolBar("Tools")
        toolbar.setIconSize(QSize(18, 18))

        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()

        self.zoom_fit = toolbar.addAction("Zoom to Fit")
        self.zoom_fit.setIcon(QIcon("icons/zoom-fit.png"))
        self.zoom_fit.triggered.connect(self.view.toggle_zoom_to_fit)
        self.zoom_fit.setCheckable(True)
        self.zoom_in.setIcon(QIcon("icons/zoom-in.png"))
        self.zoom_out.setIcon(QIcon("icons/zoom-out.png"))
        toolbar.addAction(self.zoom_in)
        toolbar.addAction(self.zoom_out)

        toolbar.addSeparator()
        tools_menu = self.menuBar().addMenu("&Tools")
        toolbox = QActionGroup(self)

        self.cursor_tool = toolbar.addAction("Cursor Tool")
        self.cursor_tool.setIcon(QIcon("icons/cursor.png"))
        self.cursor_tool.setCheckable(True)
        self.cursor_tool.setChecked(True)
        self.cursor_tool.triggered.connect(partial(self._set_tool, "cursor_tool"))
        self.cursor_tool.setShortcut(QKeySequence(Qt.Key_1))
        toolbox.addAction(self.cursor_tool)
        tools_menu.addAction(self.cursor_tool)

        draw_tool = toolbar.addAction("Drawing Tool")
        draw_tool.setIcon(QIcon("icons/draw.png"))
        draw_tool.setCheckable(True)
        draw_tool.triggered.connect(partial(self._set_tool, "draw_tool"))
        draw_tool.setShortcut(QKeySequence(Qt.Key_2))
        toolbox.addAction(draw_tool)
        tools_menu.addAction(draw_tool)

        bucket_tool = toolbar.addAction("Bucket Tool")
        bucket_tool.setIcon(QIcon("icons/paint-bucket.png"))
        bucket_tool.setCheckable(True)
        bucket_tool.triggered.connect(partial(self._set_tool, "bucket_tool"))
        bucket_tool.setShortcut(QKeySequence(Qt.Key_3))
        toolbox.addAction(bucket_tool)
        tools_menu.addAction(bucket_tool)

        move_tool = toolbar.addAction("Contour Tool")
        move_tool.setIcon(QIcon("icons/contour-tool.png"))
        move_tool.setCheckable(True)
        move_tool.triggered.connect(partial(self._set_tool, "contour_tool"))
        move_tool.setShortcut(QKeySequence(Qt.Key_4))
        toolbox.addAction(move_tool)
        tools_menu.addAction(move_tool)
        toolbar.addSeparator()

        morph_tool = toolbar.addAction("Morphology Tool")
        morph_tool.setIcon(QIcon("icons/fill-holes.png"))
        morph_tool.setCheckable(True)
        morph_tool.triggered.connect(partial(self._set_tool, "morphology_tool"))
        morph_tool.setShortcut(QKeySequence(Qt.Key_5))
        toolbox.addAction(morph_tool)
        tools_menu.addAction(morph_tool)

        copy_mask = toolbar.addAction("Masks Tool")
        copy_mask.setIcon(QIcon("icons/copy-content.png"))
        copy_mask.setCheckable(True)
        copy_mask.triggered.connect(partial(self._set_tool, "masks_tool"))
        copy_mask.setShortcut(QKeySequence(Qt.Key_6))
        toolbox.addAction(copy_mask)
        tools_menu.addAction(copy_mask)

        toolbar.addSeparator()

    def _add_edit_menu(self, scene):
        self.edit_menu.clear()
        self.undo_action = scene.create_undo_action()
        self.undo_action.setShortcuts(QKeySequence.Undo)
        self.redo_action = scene.create_redo_action()
        self.redo_action.setShortcuts(QKeySequence.Redo)
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)

    def closeEvent(self, event):
        if self._ask_before_closing:
            value = self._confirm_close_project()
            if value == QMessageBox.Cancel:
                event.ignore()
                return
            elif value == QMessageBox.Save:
                self._save_to_disk()

        settings.set_window_position(self)
        settings.set_last_opened_image(self.inspector.current_image)
        super().closeEvent(event)
