from krita import Extension, Krita

from .resizer import Resizer


class SubwindowOrganizer(Extension):

    def __init__(self, parent):
        super(SubwindowOrganizer, self).__init__(parent)
        self._is_toggled = False
        self._is_subwindow_on = False  # true if subwindows are on
        self._resizer: Resizer

    def pick_subwindow(self):
        # switching between subwindows - user action
        if not self._resizer.subWindowFilterAll.isMaximized:
            self._resizer.user_toggle_subwindow()

    def open_overview(self):
        # opens grayscale overview
        self._resizer.user_open_overview()

    def organizer_toggle(self, toggled):
        # toggles the whole plugin off and on
        Krita.instance().writeSetting("SubwindowOrganizer",
                                      "organizerToggled", str(toggled).lower())
        self._is_toggled = toggled
        if self._is_subwindow_on and self._is_toggled:
            self.pickSubwindowAction.setVisible(True)
            self.openOverviewAction.setVisible(True)
            self._resizer.user_turn_on()
        else:
            self.pickSubwindowAction.setVisible(False)
            self.openOverviewAction.setVisible(False)
            self._resizer.user_turn_off()

    def setup(self):
        # reading values saved in krita settings and creating a notifier for settings changed event
        if Krita.instance().readSetting("SubwindowOrganizer", "organizerToggled", "true") == "true":
            self._is_toggled = True
        if Krita.instance().readSetting("", "mdi_viewmode", "1") == "0":
            self._is_subwindow_on = True

        self.settingsNotifier = Krita.instance().notifier()
        self.settingsNotifier.setActive(True)
        self.settingsNotifier.configurationChanged.connect(
            self.on_settings_changed)

    def on_settings_changed(self):
        # happens when document mode (subwindow and tabs) is changed in settings by the user
        if Krita.instance().readSetting("", "mdi_viewmode", "1") == "0":
            newMode = True
        else:
            newMode = False

        if self._is_subwindow_on ^ newMode:  # mode was changed in krita settings
            self._is_subwindow_on = newMode
            if self._is_subwindow_on:  # changed from tabs to subwindows
                # addon now can be activated and deactivated
                self.organizerToggleAction.setVisible(True)
                if self._is_toggled:  # addon is on, so we can activate it
                    self._resizer.user_turn_on()
            else:  # mode changed from subwindows to tab
                self.organizerToggleAction.setVisible(False)
                if self._is_toggled:  # addon was on
                    self._resizer.user_turn_off()

    def createActions(self, window):
        # creates actions displayed in the view menu
        qwin = window.qwindow()
        toggleAtStart = self._is_toggled and self._is_subwindow_on
        self._resizer = Resizer(qwin, toggleAtStart)

        self.organizerToggleAction = window.createAction(
            "organizerToggle", "Toggle organizer", "view")
        self.organizerToggleAction.setCheckable(True)
        self.organizerToggleAction.setChecked(self._is_toggled)
        self.organizerToggleAction.toggled.connect(self.organizer_toggle)
        self.organizerToggleAction.setVisible(self._is_subwindow_on)

        self.pickSubwindowAction = window.createAction(
            "pickSubwindow", "Pick subwindow", "view")
        self.pickSubwindowAction.triggered.connect(self.pick_subwindow)
        self.pickSubwindowAction.setVisible(False)

        self.openOverviewAction = window.createAction(
            "openOverview", "Open canvas overview", "view")
        self.openOverviewAction.triggered.connect(self.open_overview)
        self.openOverviewAction.setVisible(False)


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
