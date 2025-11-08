from krita import *
from copy import copy

from .config import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .resizer import Resizer

# event catcher for windows on back


class SubwindowFilterBackground(QMdiSubWindow):
    def __init__(self, resizer: "Resizer", parent=None):
        super().__init__(parent)
        self.resizer = resizer
        self._reset_flags()

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Resize:
            self.resizer.move_subwindows()  # update the second window

        elif e.type() == QEvent.WindowStateChange:  # title bar buttons override
            oldMinimized = False
            if int(e.oldState()) & int(Qt.WindowMinimized) != 0:
                oldMinimized = True

            if obj.isMinimized():  # minimize button toggled - discard all changes
                if obj.isMaximized():
                    obj.showMaximized()
                else:
                    obj.showNormal()
                return True

            if not obj.isMinimized() and oldMinimized:  # ?
                return True

            if self.resizer.views == 1:  # to make sure
                obj.showMaximized()

        elif e.type() == QEvent.MouseButtonPress:
            cursorLocal = e.pos()  # cursor in relation to window
            if -25 < cursorLocal.x() < 25 or obj.width()-25 < cursorLocal.x() < obj.width()+25 \
                    or -3 < cursorLocal.y() < 3 or obj.height()-25 < cursorLocal.y() < obj.height()+25:  # it is a resize, not move
                self.resizeBool = True
            else:
                self.resizeBool = False

        elif e.type() == QEvent.MouseButtonRelease:
            self.cursor = self.resizer.mdiArea.mapFromGlobal(
                e.globalPos())  # self.cursor in relation to mdiarea
            self.lastCursorReleased = copy(self.cursor)

        elif e.type() == QEvent.Move:
            if (not self.resizeBool) and not self.switchingInProgress and self.cursor != None:
                self.switchingInProgress = True

                done = self._swap_floaters(obj)
                if not done:
                    done = self._swap_backgrounders(obj)
                if not done:
                    # go out of split mode on mouse on bottom
                    done = self._enter_one_window_mode(obj)
                # entering split mode is done by floaters movement

            self._reset_flags()
            return True

        return False

    def _is_under_mouse(self, subwindow, cursor):
        if subwindow.pos().x() < cursor.x() < subwindow.pos().x() + subwindow.width() \
                and subwindow.pos().y() < cursor.y() < subwindow.pos().y() + subwindow.height():
            return True
        return False

    # these flags make sure that the move event was caused by mouse input, not script
    def _reset_flags(self):
        self.resizeBool = False
        self.cursor = None
        self.switchingInProgress = False

    # drag and drop action for swapping a background window with floater
    def _swap_floaters(self, obj):
        for subwindow in self.resizer.mdiArea.subWindowList():  # swapping with floaters
            if self._is_under_mouse(subwindow, self.cursor) and subwindow != obj:
                if subwindow != self.resizer.activeSubwin and subwindow != self.resizer.otherSubwin and not subwindow.isMinimized():  # other floater, swap with it
                    if obj == self.resizer.activeSubwin:
                        self.resizer.switch_background_and_floater(
                            self.resizer.activeSubwin, subwindow)
                    else:
                        self.resizer.switch_background_and_floater(
                            self.resizer.otherSubwin, subwindow)

                    x = obj.pos().x()
                    y = obj.pos().y()
                    sX = obj.width()
                    sY = obj.height()
                    self.resizer.resize_floater(obj)
                    sX -= obj.width()
                    sY -= obj.height()

                    print(sX, sY)

                    # snapping to border, if got smaller and was on bottom or right
                    # closer to the right border of canvas than left one
                    if x > self.resizer.mdiArea.width() - obj.width() - x:
                        x += sX  # self.resizer.mdiArea.width() - sX
                    # closer to the right border of canvas than left one
                    if y > self.resizer.mdiArea.height() - obj.height() - y:
                        y += sY  # self.resizer.mdiArea.height() - sY
                    obj.move(x, y)

                    return True
        return False

    # drag and drop action for swapping two background windows
    def _swap_backgrounders(self, obj):
        for subwindow in self.resizer.mdiArea.subWindowList():  # swapping backgrounders
            if self._is_under_mouse(subwindow, self.cursor) and subwindow != obj:
                if subwindow == self.resizer.activeSubwin or subwindow == self.resizer.otherSubwin:  # other background window - swap
                    self.resizer.switch_background_windows()
                    self.resizer.move_subwindows()
                    return True
        return False

    # drag and drop action for leaving split screen mode
    def _enter_one_window_mode(self, obj):
        if self.resizer.refNeeded and obj in [self.resizer.activeSubwin, self.resizer.otherSubwin] \
                and 200 < self.cursor.y() < self.resizer.mdiArea.height() - 10 \
                and 5 < self.cursor.x() < self.resizer.mdiArea.width() - 5:  # in mdiArea

            if obj == self.resizer.activeSubwin:
                temp = self.resizer.activeSubwin
                self.resizer.activeSubwin = self.resizer.otherSubwin
                self.resizer.otherSubwin = temp

            self.resizer.user_mode_one_window()
            obj.move(self.lastCursorReleased.x() - 0.5 *
                     obj.width(), self.lastCursorReleased.y() - 10)
            return True
        return False
