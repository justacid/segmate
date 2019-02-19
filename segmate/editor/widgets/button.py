from PySide2.QtWidgets import QPushButton


class Button(QPushButton):

    def __init__(self, label, *, callback=None):
        super().__init__(label)
        if callback is not None:
            self.pressed.connect(callback)
