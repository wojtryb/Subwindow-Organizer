from threading import Lock

from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QWindowStateChangeEvent
from PyQt5.QtWidgets import QMdiSubWindow


class SubwindowFilter(QMdiSubWindow):

    def __init__(self):
        super().__init__()
        self._lock = Lock()
        self._maximize_states: dict[QMdiSubWindow, bool] = {}

    def eventFilter(self, subwindow: QMdiSubWindow, event: QEvent):
        if self._lock.locked():
            return False

        with self._lock:
            # minimize and maximize actions
            if isinstance(event, QWindowStateChangeEvent):
                if subwindow not in self._maximize_states:
                    self._maximize_states[subwindow] = False

                was_maximized = self._maximize_states[subwindow]
                is_maximized = subwindow.isMaximized()

                if is_maximized and not was_maximized:
                    print("MAXIMIZED")
                if not is_maximized and was_maximized:
                    print("MINIMIZED")

                self._maximize_states[subwindow] = is_maximized

            elif event.type() == QEvent.Type.Resize:
                # print(f"---Window Resize {subwindow}")
                # subwindow.resize(400, 400)
                pass

            elif event.type() == QEvent.Type.MouseButtonPress:
                # print(f"---Window Mouse Button Press {obj}")
                pass

            elif event.type() == QEvent.Type.MouseButtonRelease:
                # print(f"---Window Mouse Button Release {obj}")
                pass

            elif event.type() == QEvent.Type.Move:
                # print(f"---Window Move {subwindow}")
                # subwindow.move(200, 200)
                pass

        return False
