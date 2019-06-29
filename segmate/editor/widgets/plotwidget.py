import warnings

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavBar,
    FigureCanvas,
)


class WrappedCanvas(FigureCanvas):

    def draw(self):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                super().draw()
        except:
            pass


class MatplotWidget(QWidget):

    def __init__(self, parent=None, *, show_navbar=True):
        super().__init__(parent)

        mpl.rcParams.update({
            "text.color": "white",
            "axes.labelcolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "font.size": 8
        })

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(facecolor="none")
        self.canvas = WrappedCanvas(self.figure)
        self.setStyleSheet("background-color:palette(alternate-base);")

        layout.addWidget(self.canvas)
        if not show_navbar:
            return

        navbar = NavBar(self.canvas, self, coordinates=False)
        navbar_container = QWidget()
        navbar_container.setContentsMargins(0, 0, 0, 0)
        navbar_container.setFixedHeight(50)

        navbar_layout = QHBoxLayout(navbar_container)
        navbar_layout.addWidget(navbar)
        navbar_layout.setAlignment(navbar, Qt.AlignCenter)
        layout.addWidget(navbar_container)
