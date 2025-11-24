from PyQt5.QtWidgets import QMdiSubWindow

from .subwindow_filter import SubwindowFilter
from .subwindow_to_do import SubwindowToDo
from .mdi_area_filter import MdiAreaFilter
from .resizer import Resizer


class MdiAreaToDo(MdiAreaFilter.ToDo):
    def __init__(self, resizer: Resizer) -> None:
        self._resizer = resizer
        self._subwindow_filter = SubwindowFilter(SubwindowToDo(resizer))

    def on_subwindow_open(self, subwindow: QMdiSubWindow):
        print(f"View Opened: {subwindow}")
        subwindow.installEventFilter(self._subwindow_filter)

    def on_subwindow_close(self, subwindow: QMdiSubWindow):
        print(f"View Closed: {subwindow}")
        subwindow.removeEventFilter(self._subwindow_filter)
