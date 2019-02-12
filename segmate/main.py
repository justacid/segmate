import os
import sys

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt

from segmate.app import Application
from segmate.theme import darktheme
from segmate.widgets import MainWindowWidget


def main():
    real_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(real_path)

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = Application(sys.argv)
    darktheme.apply(app)

    window = MainWindowWidget()
    app.tablet_active.connect(window.view.tabletActive)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
