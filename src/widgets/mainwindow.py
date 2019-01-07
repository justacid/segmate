from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .inspectorwidget import InspectorWidget
from .viewwidget import ViewWidget
from dataloader import DataLoader
from editor import EditorScene


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi()
        self.setPosition()
        self.addMenu()
        self.addToolBar()

        args = QApplication.arguments()
        if len(args) > 1:
            self.openFolder(args[1])

    def setupUi(self):
        self.statusBar().showMessage("Ready")
        self.setWindowIcon(QIcon("icons/app-icon.png"))

        self.view = ViewWidget()
        self.view.setAlignment(Qt.AlignCenter)
        self.view.zoom_changed.connect(self.zoomChanged)
        self.view.fitview_changed.connect(self.fitChanged)
        self.setCentralWidget(self.view)

        self.inspector = InspectorWidget()
        self.inspector.scene_changed.connect(lambda x: self.view.setScene(x))

        self.dock = QDockWidget("Inspector")
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock.setMinimumSize(250, 344)
        self.dock.setWidget(self.inspector)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    def setPosition(self):
        screen = QDesktopWidget(self).availableGeometry()
        size = screen.width() * 0.75, screen.height() * 0.75
        self.resize(*size)
        self.move((screen.width() - size[0]) / 2, (screen.height() - size[1]) / 2)

    def addMenu(self):
        self.quit_action = QAction("&Quit")
        self.quit_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q))
        self.quit_action.triggered.connect(QApplication.quit)

        self.open_action = QAction("&Open Folder")
        self.open_action.setIcon(QIcon("icons/open-folder.png"))
        self.open_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.open_action.triggered.connect(self.openFolderDialog)

        self.save_action = QAction("&Save Current")
        self.save_action.setIcon(QIcon("icons/save-current.png"))
        self.save_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        self.save_action.triggered.connect(lambda: print("SAVE!"))

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        self.fitview_action = QAction("Zoom to &Fit")
        self.fitview_action.setCheckable(True)
        self.fitview_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_F))
        self.fitview_action.triggered.connect(lambda: self.view.toggleZoomToFit())

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
            action.triggered.connect(partial(lambda z: self.view.setZoom(z), zoom))
            action.setCheckable(True)
            if zoom == 100:
                action.setChecked(True)
            zoom_submenu.addAction(action)

        custom_zoom = self.zoom_group.addAction(f"Custom")
        custom_zoom.setCheckable(True)
        zoom_submenu.addAction(custom_zoom)

    def addToolBar(self):
        toolbar = super().addToolBar("Tools")
        toolbar.setMovable(False)

        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()

        self.zoom_fit = toolbar.addAction("Zoom to Fit")
        self.zoom_fit.setIcon(QIcon("icons/zoom-fit.png"))
        self.zoom_fit.triggered.connect(self.view.toggleZoomToFit)
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
        self.toolbox = QActionGroup(self)
        cursor_tool = toolbar.addAction("Cursor Tool")
        cursor_tool.setIcon(QIcon("icons/cursor.png"))
        cursor_tool.setCheckable(True)
        cursor_tool.setChecked(True)
        cursor_tool.triggered.connect(partial(self.setTool, "cursor_tool"))
        cursor_tool.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_1))
        self.toolbox.addAction(cursor_tool)
        move_tool = toolbar.addAction("Contour Tool")
        move_tool.setIcon(QIcon("icons/move-control-point.png"))
        move_tool.setCheckable(True)
        move_tool.triggered.connect(partial(self.setTool, "move_tool"))
        move_tool.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_2))
        self.toolbox.addAction(cursor_tool)
        self.toolbox.addAction(move_tool)
        draw_tool = toolbar.addAction("Drawing Tool")
        draw_tool.setIcon(QIcon("icons/draw.png"))
        draw_tool.setCheckable(True)
        draw_tool.triggered.connect(partial(self.setTool, "draw_tool"))
        draw_tool.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_3))
        self.toolbox.addAction(draw_tool)
        magic_wand = toolbar.addAction("Magic Wand Tool")
        magic_wand.setIcon(QIcon("icons/magic-wand.png"))
        magic_wand.setCheckable(True)
        magic_wand.triggered.connect(partial(self.setTool, "magicwand_tool"))
        magic_wand.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_4))
        self.toolbox.addAction(magic_wand)
        toolbar.addSeparator()

    def setTool(self, tool):
        for layer in self.view.scene().layers:
            callback = lambda msg: self.statusBar().showMessage(msg, 2000)
            layer.setTool(tool, status_callback=callback)

    def openFolder(self, folder):
        self.inspector.setScene(EditorScene(DataLoader(folder)))
        self.inspector.changeImage(0)

    def openFolderDialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Directory...", "/home")
        if folder:
            self.openFolder(folder)

    def zoomChanged(self, zoom):
        try:
            idx = self.zoom_levels.index(zoom)
            self.zoom_group.actions()[idx].setChecked(True)
        except ValueError:
            self.zoom_group.actions()[-1].setChecked(True)
            self.zoom_group.actions()[-1].setText(f"Custom {zoom}%")

        message = f"Zoom: {zoom}%"
        self.statusBar().showMessage(message, 2000)

    def fitChanged(self, toggled_on):
        if toggled_on:
            self.statusBar().showMessage("Zoom to fit: On")
            self.zoom_fit.setChecked(True)
        if not toggled_on:
            self.statusBar().showMessage("Zoom to fit: Off", 2000)
            self.zoom_fit.setChecked(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.inspector.showNextImage()
            return
        elif event.key() == Qt.Key_Left:
            self.inspector.showPreviousImage()
            return

        event.ignore()
