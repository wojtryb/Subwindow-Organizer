from krita import Extension, Krita

from PyQt5.QtWidgets import QMdiArea

from filters import MdiAreaFilter
from logic import MdiAreaLogic, Resizer


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
            MdiAreaLogic(Resizer(mdiArea)))
