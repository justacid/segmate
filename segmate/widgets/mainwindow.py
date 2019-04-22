from functools import partial
from os.path import isdir, isfile

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import segmate
from segmate.widgets.inspector import InspectorWidget
from segmate.widgets.sceneview import SceneViewWidget
from segmate.store import DataStore
from segmate.editor import EditorScene, registry
from segmate.project import ProjectDialog, ProjectFile


class MainWindowWidget(QMainWindow):

    def __init__(self):
        super().__init__()
        self._active_tool = "cursor_tool"
        self._recent_tool = None
        self._active_project = ""
        self._ask_before_closing = False

        self._setup_ui()
        self._add_menu()
        self._add_tool_bar()
        self._restore_window_position()
        self._load_last_opened()
        self._first_load()
        self._set_window_title()

    def _set_window_title(self, modified=False):
        title = f"Segmate {segmate.__version__} "
        project = "" if not self._active_project else f"- {self._active_project}"
        modified = f" {'(*)' if modified else ''}"
        self.setWindowTitle(f"{title}{project}{modified}")

    def _restore_window_position(self):
        screen = QDesktopWidget(self).availableGeometry()
        default_size = screen.width() * 0.75, screen.height() * 0.75
        default_pos = (screen.width() - default_size[0]) / 2, \
            (screen.height() - default_size[1]) / 2

        settings = QSettings("justacid", "Segmate")
        settings.beginGroup("MainWindow")
        size = settings.value("size", QSize(*default_size))
        pos = settings.value("position", QPoint(*default_pos))
        is_maximized = settings.value("maximized", "false")
        settings.endGroup()

        if is_maximized == "true":
            self.setWindowState(self.windowState() | Qt.WindowMaximized)
            return

        self.resize(size)
        self.move(pos)

    def _first_load(self):
        settings = QSettings("justacid", "Segmate")
        settings.beginGroup("Warning")
        show_warning = settings.value("was_shown", "false")
        if show_warning == "false":
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Information")
            msgbox.setText("Editing is destructive!")
            p1 = "Editing images is a destructive operation."
            p2 = "Please make sure to make a backup of your data before using Segmate!"
            msgbox.setInformativeText(f"{p1} {p2}")
            msgbox.setIcon(QMessageBox.Information)
            msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgbox.setDefaultButton(QMessageBox.Cancel)

            value = msgbox.exec()
            if value == QMessageBox.Ok:
                settings.setValue("was_shown", True)
        settings.endGroup()

    def _load_last_opened(self):
        settings = QSettings("justacid", "Segmate")
        settings.beginGroup("Project")
        self._active_project = settings.value("last_opened", "")
        if not isfile(self._active_project):
            return
        last_image_shown = settings.value("last_image", 0)
        if self._active_project:
            project = ProjectFile.parse(self._active_project)
            self._open_project(self._active_project, project)
            self.inspector.slider.setValue(int(last_image_shown))
        settings.endGroup()
        self._set_window_title()

    def _open_project(self, spf_path, project):
        if isdir(project.data_root):
            store = DataStore.from_project(project)
            self.inspector.set_scene(EditorScene(store))
            self.inspector.scene.image_modified.connect(self._mark_dirty)
            self.inspector.change_image(0)
            self.close_action.setEnabled(True)
            self._active_project = spf_path
        else:
            self._active_project = ""
        self._set_window_title()
        settings = QSettings("justacid", "Segmate")
        settings.beginGroup("Project")
        settings.setValue("last_opened", self._active_project)
        settings.setValue("last_image", 0)
        settings.endGroup()

    def _close_project(self):
        if self._ask_before_closing:
            value = self._confirm_close()
            if value == QMessageBox.Cancel:
                return
            elif value == QMessageBox.Save:
                self._save_to_disk()

        self._ask_before_closing = False
        del self.view.scene().data_store
        self.view.setScene(None)
        self.inspector.set_scene(None)
        self.close_action.setEnabled(False)
        settings = QSettings("justacid", "Segmate")
        settings.beginGroup("Project")
        settings.setValue("last_opened", "")
        settings.setValue("last_image", 0)
        settings.endGroup()
        self._active_project = ""
        self._set_window_title()

    def _open_project_dialog(self):
        if self._ask_before_closing:
            value = self._confirm_close()
            if value == QMessageBox.Cancel:
                return
            elif value == QMessageBox.Save:
                self._save_to_disk()

        self._ask_before_closing = False
        home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        filename = QFileDialog.getOpenFileName(
            self, "Open Project", home, "Segmate Project File (*.spf)")
        if filename[0]:
            project = ProjectFile.parse(filename[0])
            self._open_project(filename[0], project)
            self.close_action.setEnabled(True)

    def _new_project_dialog(self):
        if self._ask_before_closing:
            value = self._confirm_close()
            if value == QMessageBox.Cancel:
                return
            elif value == QMessageBox.Save:
                self._save_to_disk()

        dialog = ProjectDialog(self)
        if dialog.exec() == QDialog.Rejected:
            return

        project = ProjectFile()
        project.data_root = dialog.data_root
        project.folders = dialog.folders
        project.masks = dialog.masks
        project.editable = dialog.editable
        project.colors = dialog.colors

        self._ask_before_closing = False
        ProjectFile.save(dialog.project_path, project)
        self._open_project(dialog.project_path, project)

    def _confirm_close(self):
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

    def _scene_changed(self, scene):
        self.view.setScene(scene)
        self._add_edit_menu(scene)

    def _retain_active_tool(self):
        last_used = self._recent_tool
        self._set_tool(self._active_tool)
        self._recent_tool = last_used

    def _set_tool(self, tool):
        if self._active_tool == tool:
            return
        self._recent_tool = self._active_tool
        self._active_tool = tool
        if self.view.scene() is None or not self.view.scene().layers:
            return
        for layer in self.view.scene().layers:
            callback = lambda msg: self.statusBar().showMessage(msg, 2000)
            layer.change_tool(tool, status_callback=callback)
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
        try:
            idx = self.zoom_levels.index(zoom)
            self.zoom_group.actions()[idx].setChecked(True)
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
        self.inspector.image_changed.connect(self._retain_active_tool)

        self.dock = QDockWidget("Inspector")
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock.setMinimumWidth(275)
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
        view_menu.addAction(self.dock.toggleViewAction())
        view_menu.addSeparator()
        view_menu.addAction(self.fitview_action)
        zoom_submenu = view_menu.addMenu("Zoom")

        self.zoom_group = QActionGroup(zoom_submenu)
        self.zoom_group.setExclusive(True)
        self.zoom_levels = list(range(20, 320, 20))

        for zoom in self.zoom_levels:
            action = self.zoom_group.addAction(f"{zoom}%")
            action.triggered.connect(partial(lambda z: self.view.set_zoom(z), zoom))
            action.setCheckable(True)
            if zoom == 100:
                action.setChecked(True)
            zoom_submenu.addAction(action)

        custom_zoom = self.zoom_group.addAction(f"Custom")
        custom_zoom.setCheckable(True)
        zoom_submenu.addAction(custom_zoom)

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
        zoom_in = toolbar.addAction("Zoom In")
        zoom_in.setIcon(QIcon("icons/zoom-in.png"))
        zoom_in.triggered.connect(partial(self.view.zoom, 10))
        zoom_in.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Equal))
        zoom_out = toolbar.addAction("Zoom Out")
        zoom_out.setIcon(QIcon("icons/zoom-out.png"))
        zoom_out.triggered.connect(partial(self.view.zoom, -10))
        zoom_out.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus))

        toolbar.addSeparator()
        tools_menu = self.menuBar().addMenu("&Tools")
        toolbox = QActionGroup(self)

        cursor_tool = toolbar.addAction("Cursor Tool")
        cursor_tool.setIcon(QIcon("icons/cursor.png"))
        cursor_tool.setCheckable(True)
        cursor_tool.setChecked(True)
        cursor_tool.triggered.connect(partial(self._set_tool, "cursor_tool"))
        cursor_tool.setShortcut(QKeySequence(Qt.Key_1))
        toolbox.addAction(cursor_tool)
        tools_menu.addAction(cursor_tool)

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
            value = self._confirm_close()
            if value == QMessageBox.Cancel:
                event.ignore()
                return
            elif value == QMessageBox.Save:
                self._save_to_disk()

        is_maximized = self.windowState() == Qt.WindowMaximized
        settings = QSettings("justacid", "Segmate")
        settings.beginGroup("MainWindow")
        if not is_maximized:
            settings.setValue("size", self.size())
            settings.setValue("position", self.pos())
        settings.setValue("maximized", is_maximized)
        settings.endGroup()
        settings.beginGroup("Project")
        settings.setValue("last_image", self.inspector.current_image)
        settings.endGroup()
        super().closeEvent(event)
