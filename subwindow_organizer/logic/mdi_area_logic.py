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
        self._resizer.background_resizer.add(subwindow)

        if len(self._resizer.mdi_area.subWindowList()) >= 3:
            self._resizer.resize_to_suggested_size(subwindow)

    def on_subwindow_close(self, subwindow: QMdiSubWindow):
        subwindow.removeEventFilter(self._subwindow_filter)
        self._resizer.background_resizer.remove(subwindow)
