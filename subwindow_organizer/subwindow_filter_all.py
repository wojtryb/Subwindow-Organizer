from krita import Krita

from .config import MINIMALCOLUMNWIDTH

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QMdiSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .resizer import Resizer


class SubwindowFilterAll(QMdiSubWindow):
    # event catcher for every window - both floaters and back ones

    def __init__(self, resizer: "Resizer", parent=None):
        super().__init__(parent)
        self.resizer = resizer

        self.isMaximized = False  # is any window currently maximized

    def eventFilter(self, obj, e):
        # override krita minimize and maximize actions
        if e.type() == QEvent.Type.WindowStateChange:
            # prevent freeze on user changing krita windows mode
            if Krita.instance().readSetting("", "mdi_viewmode", "1") == "0":
                oldMaximized = False
                if int(e.oldState()) & int(Qt.WindowState.WindowMaximized) != 0:
                    oldMaximized = True

                if obj.isMaximized() and not oldMaximized:  # there was a change to maximized state
                    self._hide_all_except(self.resizer, exception=obj)
                    self.isMaximized = True
                if not obj.isMaximized() and oldMaximized:  # there was a change to normal from maximize
                    self._show_all(self.resizer)
                    self.isMaximized = False

        # krita will crush if there will be a maximized window in usual close handling - it has to be made normal before it
        if e.type() == QEvent.Type.Close:  # dont seem to work anyway...
            obj.showNormal()
            self._show_all(self.resizer)
            self.isMaximized = False

        return False

    def _hide_all_except(self, resizer: "Resizer", exception):
        # hiding windows, when one gets maximized
        for subwindow in resizer.mdiArea.subWindowList():
            if subwindow != exception:
                subwindow.hide()
        if resizer.activeSubwin is not None:
            # minimal width would not allow them to hide properly
            resizer.activeSubwin.setMinimumWidth(0)
        if resizer.otherSubwin is not None:
            resizer.otherSubwin.setMinimumWidth(0)

    def _show_all(self, resizer: "Resizer"):
        # show all hidden window, when maximized turns normal
        for subwindow in resizer.mdiArea.subWindowList():
            subwindow.show()
        if resizer.activeSubwin is not None:
            resizer.activeSubwin.setMinimumWidth(
                MINIMALCOLUMNWIDTH)  # getting minimal width again
        if resizer.otherSubwin is not None:
            resizer.otherSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH)
