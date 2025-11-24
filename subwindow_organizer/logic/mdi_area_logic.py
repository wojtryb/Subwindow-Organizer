from PyQt5.QtWidgets import QMdiSubWindow

from filters import MdiAreaFilter, SubwindowFilter
from .subwindow_logic import SubwindowLogic
from .resizer import Resizer


class MdiAreaLogic(MdiAreaFilter.Logic):
    def __init__(self, resizer: Resizer) -> None:
        self._resizer = resizer
        self._subwindow_filter = SubwindowFilter(SubwindowLogic(resizer))

    def on_subwindow_open(self, subwindow: QMdiSubWindow):
        print(f"View Opened: {subwindow}")
        subwindow.installEventFilter(self._subwindow_filter)

    def on_subwindow_close(self, subwindow: QMdiSubWindow):
        print(f"View Closed: {subwindow}")
        subwindow.removeEventFilter(self._subwindow_filter)
