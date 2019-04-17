from PySide2.QtCore import Qt, QEvent


class MouseButtons:

    def __init__(self, qevent):
        self._qevent = qevent

    @property
    def left(self):
        if self._qevent.buttons() & Qt.LeftButton:
            return True
        return self._qevent.button() == Qt.LeftButton

    @property
    def middle(self):
        if self._qevent.buttons() & Qt.MidButton:
            return True
        return self._qevent.button() == Qt.MidButton

    @property
    def right(self):
        if self._qevent.buttons() & Qt.RightButton:
            return True
        return self._qevent.button() == Qt.RightButton


class MouseEvent:

    def __init__(self, qevent):
        self._qevent = qevent
        self.buttons = MouseButtons(qevent)

    @property
    def pos(self):
        return (self._qevent.pos().y(), self._qevent.pos().x())

    @property
    def shift(self):
        if self._qevent.modifiers() & Qt.ShiftModifier:
            return True
        return False

    @property
    def ctrl(self):
        if self._qevent.modifiers() & Qt.ControlModifier:
            return True
        return False


class Key:

    def __init__(self, qevent):
        self._qevent = qevent

    def __getattr__(self, key):
        try:
            key = getattr(Qt, key)
        except:
            raise AttributeError(f"type object 'Key' has no attribute '{key}'")
        return self._qevent.key() == key


class KeyEvent:

    def __init__(self, qevent):
        self._qevent = qevent
        self.key = Key(qevent)

    @property
    def shift(self):
        if self._qevent.modifiers() & Qt.ShiftModifier:
            return True
        return False

    @property
    def ctrl(self):
        if self._qevent.modifiers() & Qt.ControlModifier:
            return True
        return False
