from PyQt5.QtWidgets import QMdiSubWindow

from filters import MdiAreaFilter, SubwindowFilter
from .subwindow_logic import SubwindowLogic
from .resizer import Resizer


class MdiAreaLogic(MdiAreaFilter.Logic):
    def __init__(self, resizer: Resizer) -> None:
        self._resizer = resizer
        self._subwindow_filter = SubwindowFilter(SubwindowLogic(resizer))
        self._background_windows = set()

    def on_subwindow_open(self, subwindow: QMdiSubWindow):
        subwindow.installEventFilter(self._subwindow_filter)

        amount = len(self._resizer.mdi_area.subWindowList())

        if amount == 1:
            self._resizer.left = subwindow
            self._resizer.right = None
            self._resizer.resize_background_subwindows()
        elif amount == 2:
            self._resizer.right = subwindow
            self._resizer.resize_background_subwindows()
        else:
            self._resizer.resize_to_suggested_size(subwindow)

    def on_subwindow_close(self, subwindow: QMdiSubWindow):
        subwindow.removeEventFilter(self._subwindow_filter)

        if subwindow == self._resizer.left:
            self._resizer.left = self._resizer.right
            self._resizer.right = None
            self._resizer.resize_background_subwindows()
        elif subwindow == self._resizer.right:
            self._resizer.right = None
            self._resizer.resize_background_subwindows()
