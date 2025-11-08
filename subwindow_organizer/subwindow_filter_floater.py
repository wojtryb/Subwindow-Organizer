from krita import Krita
from .config import SPLITMODERANGE

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QMdiSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .resizer import Resizer


# event catcher for floating windows
class SubwindowFilterFloater(QMdiSubWindow):
    def __init__(self, resizer: "Resizer", parent=None):
        super().__init__(parent)
        self.resizer = resizer
        self.resizeBool = False
        self.cursor = None
        self.switchingInProgress = False

    def eventFilter(self, obj, e: QEvent):

        if e.type() == QEvent.Type.MouseButtonPress:
            cursorLocal = e.pos()  # cursor in relation to window
            if -25 < cursorLocal.x() < 25 or obj.width()-25 < cursorLocal.x() < obj.width()+25 \
                    or -3 < cursorLocal.y() < 3 or obj.height()-25 < cursorLocal.y() < obj.height()+25:  # it is a resizeBool, not move
                self.resizeBool = True
            else:
                self.resizeBool = False

        elif e.type() == QEvent.Type.MouseButtonRelease:
            self.cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos())

            if obj.isMinimized() and e.y() < -5:  # deminimize on dragging minimized window
                obj.showNormal()
                obj.move(round(self.cursor.x() - 0.5*obj.width()),
                         round(self.cursor.y() - 10))  # move to cursor position

        elif e.type() == QEvent.Type.Move:
            # prevent freeze on user changing krita windows mode
            if Krita.instance().readSetting("", "mdi_viewmode", "1") == "0":
                # drag and drop action - going into split mode
                if self.cursor is not None and not self.resizer.refNeeded and not self.resizeBool\
                        and (self.cursor.x() < 5 or self.cursor.x() > self.resizer.mdiArea.width() - 5):

                    if self.cursor.x() < 5:  # left edge
                        self.resizer.refPosition = "left"
                    else:
                        self.resizer.refPosition = "right"

                    h = self.resizer.mdiArea.height()
                    if SPLITMODERANGE[0] * h < self.cursor.y() < SPLITMODERANGE[1] * h:
                        self.switchingInProgress = True
                        self.resizer.user_mode_split()
                        self.switchingInProgress = False
                        self.cursor = None
                        return True

                # drag and dtop action for minimizing the window
                if self.cursor is not None and not self.resizeBool and self.cursor.y() > self.resizer.mdiArea.height() - 5:
                    obj.showMinimized()
                    return True

                # snap to border when floater moves
                self.resizer.snap_to_border(obj)

        return False
