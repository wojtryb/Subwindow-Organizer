import sip
from typing import Protocol

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow

# NOTE: QMdiArea has Tabbed/Subwindow mode enums in it

# TODO: write similar class for handling krita main window resize


class MdiAreaFilter(QMdiArea):

    class ToDo(Protocol):
        def on_subwindow_open(self, subwindow: QMdiSubWindow): ...
        def on_subwindow_close(self, subwindow: QMdiSubWindow): ...

    class BlankToDo(ToDo):
        def on_subwindow_open(self, subwindow: QMdiSubWindow): ...
        def on_subwindow_close(self, subwindow: QMdiSubWindow): ...

    def __init__(self, mdiArea: QMdiArea, to_do: ToDo = BlankToDo()):
        super().__init__()
        self._mdiArea = mdiArea
        self._handled_views: set[QMdiSubWindow] = set()
        self._to_do = to_do

    def eventFilter(self, _, e: QEvent):
        if sip.isdeleted(self._mdiArea):
            return False

        # Event that can be (among many other) change in subwindows amount
        if e.type() in (QEvent.Type.ChildAdded, QEvent.Type.ChildRemoved):
            current_views = self._mdiArea.subWindowList()
            if len(self._handled_views) == len(current_views):
                return False

            current_views = set(current_views)

            if difference := current_views - self._handled_views:
                self._to_do.on_subwindow_open(difference.pop())
            else:
                difference = self._handled_views - current_views
                self._to_do.on_subwindow_close(difference.pop())

            self._handled_views = current_views
        return False
