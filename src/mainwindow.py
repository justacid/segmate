from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from widgets import InspectorWidget, ViewWidget
from dataloader import DataLoader
from scene import ImageScene


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi()
        self.setPosition()
        self.addMenu()

        args = QApplication.arguments()
        if len(args) > 1:
            self.openFolder(args[1])

    def setupUi(self):
        self.statusBar().showMessage("Ready")

        self.view = ViewWidget()
        self.view.setAlignment(Qt.AlignCenter)
        self.view.zoom_changed.connect(self.zoomChanged)
        self.view.fitview_changed.connect(self.fitChanged)
        self.setCentralWidget(self.view)

        self.inspector = InspectorWidget()
        self.inspector.scene_changed.connect(lambda x: self.view.setScene(x))

        self.dock = QDockWidget("Inspector")
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
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
        self.open_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.open_action.triggered.connect(self.openFolder)

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        self.fitview_action = QAction("Zoom to &Fit")
        self.fitview_action.setCheckable(True)
        self.fitview_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_F))
        self.fitview_action.triggered.connect(lambda: self.view.toggleZoomToFit())

        view_menu = self.menuBar().addMenu("&View")
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

    def openFolder(self, folder=None):
        if folder is None:
            folder = QFileDialog.getExistingDirectory(self, "Open Directory...", "/home")
        self.inspector.setScene(ImageScene(DataLoader(folder)))
        self.inspector.changeImage(0)

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
        if not toggled_on:
            self.statusBar().showMessage("Zoom to fit: Off", 2000)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.inspector.showNextImage()
            return
        elif event.key() == Qt.Key_Left:
            self.inspector.showPreviousImage()
            return

        event.ignore()
