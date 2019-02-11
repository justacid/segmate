from os.path import join, dirname, abspath
from PySide2.QtGui import QPalette, QColor


def apply(app):
    app.setStyle("Fusion")
    qss_path = join(dirname(abspath(__file__)), 'style.qss')
    with open(qss_path) as stylesheet:
        app.setStyleSheet(stylesheet.read())

    palette = QPalette()
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.Light, QColor(180, 180, 180))
    palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    palette.setColor(QPalette.Dark, QColor(35, 35, 35))
    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.Link, QColor(56, 252, 196))
    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))

    palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
    palette.setColor(QPalette.Text, QColor(200, 200, 200))
    palette.setColor(QPalette.BrightText, QColor(200, 200, 200))
    palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
    palette.setColor(QPalette.HighlightedText, QColor(200, 200, 200))
    palette.setColor(QPalette.ToolTipText, QColor(200, 200, 200))

    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    app.setPalette(palette)
