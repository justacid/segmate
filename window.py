from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from view import SegmentationView
from store import ImageScene, DataLoader
from inspector import InspectorDock, Inspector


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi()
        self.setPosition()
        self.addMenu()

        if len(QApplication.arguments()) > 1:
            self.openFolder()

    def setupUi(self):
        self.statusBar().showMessage("Ready")

        self.viewarea = SegmentationView()
        self.viewarea.setAlignment(Qt.AlignCenter)
        self.viewarea.zoom_changed.connect(self.zoomChanged)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.viewarea)
        self.setCentralWidget(self.viewarea)

        self.inspector = Inspector()
        self.inspector.scene_changed.connect(lambda x: self.viewarea.setScene(x))
        self.inspector_dock = InspectorDock(self.inspector)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)

    def setPosition(self):
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)
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

    def openFolder(self):
        args = QApplication.arguments()
        if len(args) > 1:
            folder = args[1]
        else:
            folder = QFileDialog.getExistingDirectory(self, "Open Directory...", "/home")

        loader = DataLoader(folder, subfolders=["images", "masks"])
        self.inspector.setScene(ImageScene(loader))
        self.inspector.changeImage(0)

    def zoomChanged(self, zoom):
        message = f"Zoom: {zoom * 100:.0f}%"
        self.statusBar().showMessage(message, 2000)