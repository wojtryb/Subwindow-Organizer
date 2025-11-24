from krita import Extension, Krita

from PyQt5.QtWidgets import QMdiArea

from .mdi_area_filter import MdiAreaFilter
from .resizer import Resizer
from .mdi_area_to_do import MdiAreaToDo


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

        qwin = window.qwindow()
        mdiArea: QMdiArea = qwin.centralWidget().findChild(QMdiArea)

        self.mdiAreaFilter = MdiAreaFilter(
            mdiArea,
            MdiAreaToDo(Resizer(mdiArea)))


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
