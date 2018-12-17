import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from view import SegmentationView
from store import ImageScene, DataLoader
from inspector import InspectorDock, Inspector


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._set_position()
        self._create_menus()

        self.scene = ImageScene()
        self.viewer = SegmentationView(self.scene)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.viewer)
        self.viewer.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.viewer)

        self.inspector = Inspector()
        self.inspector.image_changed.connect(self._change_image)
        self.inspector_dock = InspectorDock(self.inspector)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)

        if len(sys.argv) == 2:
            self._open_from_cmd(sys.argv[1])

    def _set_position(self):
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)
        size = screen.width() * 0.75, screen.height() * 0.75
        self.resize(*size)
        self.move((screen.width() - size[0]) / 2, (screen.height() - size[1]) / 2)

    def _create_menus(self):
        self.quit_action = QAction("&Quit")
        self.quit_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q))
        self.quit_action.triggered.connect(self._quit_application)

        self.open_action = QAction("&Open Folder")
        self.open_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.open_action.triggered.connect(self._open_folder)

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

    def _quit_application(self):
        QApplication.quit()

    def _open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Directory...", "/home")
        loader = DataLoader(folder, subfolders=["images", "masks"])
        self.scene.set_loader(loader)
        self.inspector.set_scene(self.scene)
        self.scene.set_image(0)

    def _open_from_cmd(self, folder):
        loader = DataLoader(folder, subfolders=["images", "clusters", "masks", "spores"])
        self.scene.set_loader(loader)
        self.inspector.set_scene(self.scene)
        self.scene.set_image(0)

    def _change_image(self, idx):
        if self.scene.loader:
            self.scene.set_image(idx)
