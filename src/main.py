import os
import sys

from PySide2.QtWidgets import QApplication
from mainwindow import MainWindow


MAJOR_VERSION = 0
MINOR_VERSION = 0
PATCH_VERSION = 1


if __name__ == "__main__":
    real_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(real_path)

    app = QApplication(sys.argv)
    window = MainWindow()
    version = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
    window.setWindowTitle(f"Segmate {version}")
    window.show()
    sys.exit(app.exec_())
