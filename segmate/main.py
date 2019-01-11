import os
import sys
import warnings

from PySide2.QtWidgets import QApplication
from qdarkstyle import load_stylesheet
from segmate.widgets import MainWindowWidget
import segmate

def main():
    real_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(real_path)

    app = QApplication(sys.argv)
    window = MainWindowWidget()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app.setStyleSheet(load_stylesheet(pyside=True))

    window.setWindowTitle(f"Segmate {segmate.__version__}")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
