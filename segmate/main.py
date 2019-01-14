import os
import sys
import warnings

from qdarkstyle import load_stylesheet
from segmate.tabletapplication import TabletApplication
from segmate.widgets import MainWindowWidget

def main():
    real_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(real_path)

    app = TabletApplication(sys.argv)
    window = MainWindowWidget()
    app.tablet_active.connect(window.view.tabletActive)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app.setStyleSheet(load_stylesheet(pyside=True))

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
