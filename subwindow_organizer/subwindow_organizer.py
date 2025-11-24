from krita import Extension, Krita

from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow

from .mdi_area_filter import MdiAreaFilter


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
            def on_resize(self):
                print("resize")

            def on_subwindow_open(self, subwindow: QMdiSubWindow):
                print(f"View Opened: {subwindow}")

            def on_subwindow_close(self, subwindow: QMdiSubWindow):
                print(f"View Closed: {subwindow}")

        qwin = window.qwindow()
        mdiArea: QMdiArea = qwin.centralWidget().findChild(QMdiArea)
        self.mdiAreaFilter = MdiAreaFilter(mdiArea, MyToDo())


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
