from PyQt5.QtWidgets import QMdiSubWindow

from filters import SubwindowFilter
from .resizer import Resizer


class SubwindowLogic(SubwindowFilter.Logic):
    def __init__(self, resizer: Resizer) -> None:
        self._resizer = resizer

    def on_maximize(self, subwindow: QMdiSubWindow):
        print("maximize")
        pass

    def on_demaximize(self, subwindow: QMdiSubWindow):
        print("demaximize")
        pass

    def on_resize(self, subwindow: QMdiSubWindow):
        print("resize")
        pass

    def on_move(self, subwindow: QMdiSubWindow):
        self._resizer.snap_to_border(subwindow)
