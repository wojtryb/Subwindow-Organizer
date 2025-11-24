from threading import Lock
from typing import Protocol

from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QWindowStateChangeEvent
from PyQt5.QtWidgets import QMdiSubWindow


class SubwindowFilter(QMdiSubWindow):

    class Logic(Protocol):
        def on_maximize(self, subwindow: QMdiSubWindow): ...
        def on_demaximize(self, subwindow: QMdiSubWindow): ...
        def on_resize(self, subwindow: QMdiSubWindow): ...
        def on_move(self, subwindow: QMdiSubWindow): ...

    class BlankLogic(Logic):
        def on_maximize(self, subwindow: QMdiSubWindow): ...
        def on_demaximize(self, subwindow: QMdiSubWindow): ...
        def on_resize(self, subwindow: QMdiSubWindow): ...
        def on_move(self, subwindow: QMdiSubWindow): ...

    def __init__(self, logic: Logic = BlankLogic()):
        super().__init__()
        self._lock = Lock()
        self._maximize_states: dict[QMdiSubWindow, bool] = {}
        self._logic = logic

    def eventFilter(self, subwindow: QMdiSubWindow, event: QEvent):
        if self._lock.locked():
            return False

        with self._lock:
            if isinstance(event, QWindowStateChangeEvent):
                if subwindow not in self._maximize_states:
                    self._maximize_states[subwindow] = False

                was_maximized = self._maximize_states[subwindow]
                is_maximized = subwindow.isMaximized()

                if is_maximized and not was_maximized:
                    self._logic.on_maximize(subwindow)
                if not is_maximized and was_maximized:
                    self._logic.on_demaximize(subwindow)

                self._maximize_states[subwindow] = is_maximized

            elif event.type() == QEvent.Type.Resize:
                self._logic.on_resize(subwindow)

            elif event.type() == QEvent.Type.Move:
                self._logic.on_move(subwindow)

            # elif event.type() == QEvent.Type.MouseButtonPress:
            #     pass

            # elif event.type() == QEvent.Type.MouseButtonRelease:
            #     pass

        return False
