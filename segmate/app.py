from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QEvent, Signal


class Application(QApplication):
    """
    This whole class is just an awful hack, needed since Qt for some
    reason starting at version 5.12 (5.11 works correctly) sends mouse
    press events, even when a tablet is active. When and if this gets
    fixed, this will be removed again - along with the corresonding
    tablet_active events in the scene view.
    """

    tablet_active = Signal(bool)

    def __init__(self, args):
        super().__init__(args)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    def event(self, event):
        if event.type() == QEvent.TabletEnterProximity:
            self.tablet_active.emit(True)
            return True
        if event.type() == QEvent.TabletLeaveProximity:
            self.tablet_active.emit(False)
            return False

        return super().event(event)
