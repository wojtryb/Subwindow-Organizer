from threading import Lock

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QWindowStateChangeEvent
from PyQt5.QtWidgets import QMdiSubWindow


class SubwindowFilter(QMdiSubWindow):

    def __init__(self):
        super().__init__()
        self._lock = Lock()

    def eventFilter(self, subwindow: QMdiSubWindow, event: QEvent):
        if self._lock.locked():
            return False

        with self._lock:
            # minimize and maximize actions
            if isinstance(event, QWindowStateChangeEvent):
                was_maximized = int(event.oldState()) & int(
                    Qt.WindowState.WindowMaximized) != 0

                if subwindow.isMaximized() and not was_maximized:
                    print("MAXIMIZED")

                if not subwindow.isMaximized() and was_maximized:
                    print("MINIMIZED")

                pass

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
