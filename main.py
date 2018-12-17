import sys
from PySide2.QtWidgets import QApplication
from window import MainWindow


MAJOR_VERSION = 0
MINOR_VERSION = 0
PATCH_VERSION = 1
                                                     

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    version = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
    window.setWindowTitle(f"Segmate {version}")
    window.show()

    sys.exit(app.exec_())