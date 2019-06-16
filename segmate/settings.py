from PySide2.QtCore import Qt, QSettings, QSize, QPoint
from PySide2.QtWidgets import QDesktopWidget


def window_position(window):
    screen = QDesktopWidget(window).availableGeometry()
    default_size = screen.width() * 0.75, screen.height() * 0.75
    default_pos = (screen.width() - default_size[0]) / 2, \
        (screen.height() - default_size[1]) / 2

    config = QSettings("justacid", "Segmate")
    config.beginGroup("MainWindow")
    size = config.value("size", QSize(*default_size))
    pos = config.value("position", QPoint(*default_pos))
    is_maximized = config.value("maximized", "false")
    is_maximized = True if "true" in is_maximized else False
    config.endGroup()

    return size, pos, is_maximized


def set_window_position(window):
    is_maximized = window.windowState() == Qt.WindowMaximized
    config = QSettings("justacid", "Segmate")
    config.beginGroup("MainWindow")
    if not is_maximized:
        config.setValue("size", window.size())
        config.setValue("position", window.pos())
    config.setValue("maximized", is_maximized)
    config.endGroup()


def last_opened_project():
    config = QSettings("justacid", "Segmate")
    config.beginGroup("Project")
    project = config.value("last_opened_project", "")
    config.endGroup()
    return project


def set_last_opened_project(project):
    config = QSettings("justacid", "Segmate")
    config.beginGroup("Project")
    config.setValue("last_opened_project", project)
    config.endGroup()


def last_opened_image():
    config = QSettings("justacid", "Segmate")
    config.beginGroup("Project")
    index = config.value("last_opened_image", 0)
    config.endGroup()
    return int(index)


def set_last_opened_image(index):
    config = QSettings("justacid", "Segmate")
    config.beginGroup("Project")
    config.setValue("last_opened_image", index)
    config.endGroup()
