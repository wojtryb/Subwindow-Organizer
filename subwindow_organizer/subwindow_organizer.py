from krita import Extension, Krita

from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow

from .mdi_area_filter import MdiAreaFilter
from .subwindow_filter import SubwindowFilter


class SubwindowOrganizer(Extension):

    def __init__(self, parent):
        super(SubwindowOrganizer, self).__init__(parent)

    def setup(self):
        self.settingsNotifier = Krita.instance().notifier()
        self.settingsNotifier.setActive(True)
        self.settingsNotifier.configurationChanged.connect(
            self.on_settings_changed)

    def on_settings_changed(self):
        pass

    def createActions(self, window):
        # TODO: this is probably not in createActions but whatever

        class MyToDo(MdiAreaFilter.ToDo):
            def __init__(self) -> None:
                self._subwindow_filter = SubwindowFilter()

            def on_resize(self):
                pass

            def on_subwindow_open(self, subwindow: QMdiSubWindow):
                print(f"View Opened: {subwindow}")
                subwindow.installEventFilter(self._subwindow_filter)

            def on_subwindow_close(self, subwindow: QMdiSubWindow):
                print(f"View Closed: {subwindow}")
                subwindow.removeEventFilter(self._subwindow_filter)

        qwin = window.qwindow()
        mdiArea: QMdiArea = qwin.centralWidget().findChild(QMdiArea)
        self.mdiAreaFilter = MdiAreaFilter(mdiArea, MyToDo())


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
