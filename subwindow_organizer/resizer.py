from krita import Krita
from copy import copy
import sip

from PyQt5.QtWidgets import QMdiArea
from PyQt5.QtCore import QPoint, QSize

from .mdi_area_filter import mdiAreaFilter
from .subwindow_filter_background import SubwindowFilterBackground
from .subwindow_filter_floater import SubwindowFilterFloater
from .subwindow_filter_all import SubwindowFilterAll

from .config import (
    REFPOSITION,
    SNAPDISTANCE,
    MINIMALCOLUMNWIDTH,
    DEFAULTFLOATERSIZE,
    DEFAULTCOLUMNRATIO,
    SOFTPROOFING)


class Resizer:
    # user customization

    def __init__(self, qwin, toggleAtStart):
        self.activeSubwin = None  # main canvas for drawing
        self.otherSubwin = None  # second main canvas for reference and overview
        # extension mode: 'split screen'(False) and 'one window'(True)
        self.refNeeded = False

        self.qWin = qwin

        self.mdiArea: QMdiArea = self.qWin.centralWidget().findChild(QMdiArea)
        # 0 on start - amount of opened subwindows
        self.views = len(self.mdiArea.subWindowList())
        self.refPosition = REFPOSITION

        if toggleAtStart:
            # cant be created on a start if the plugin should be off
            self.mdiAreaFilter = mdiAreaFilter(self)

        self.subWindowFilterBackground = SubwindowFilterBackground(
            self)  # installation on subwindows happens later
        self.subWindowFilterFloater = SubwindowFilterFloater(self)
        self.subWindowFilterAll = SubwindowFilterAll(self)

    def toggle_always_on_top(self, subwindow, check):
        menu = subwindow.children()[0]
        if menu.actions()[5].isChecked() ^ check:
            menu.actions()[5].trigger()

        menu.actions()[5].setVisible(False)

    # snapping floaters to border of the canvas
    def snap_to_border(self, subwindow):
        x = subwindow.pos().x()
        y = subwindow.pos().y()

        if x < SNAPDISTANCE:
            x = 0
        if y < SNAPDISTANCE:
            y = 0
        if x + subwindow.width() > self.mdiArea.width() - SNAPDISTANCE:
            x = self.mdiArea.width() - subwindow.width()
        if y + subwindow.height() > self.mdiArea.height() - SNAPDISTANCE:
            y = self.mdiArea.height() - subwindow.height()

        subwindow.move(x, y)

    def get_active_subwindow(self):
        if self.views == 1:  # subwindow is added to list before setting it to active window - have to make this if
            self.activeSubwin = self.mdiArea.subWindowList()[0]
        else:
            self.activeSubwin = self.mdiArea.activeSubWindow()
        if self.activeSubwin is not None:  # bugfix - when multiple windows are closed at once, it can get here with both views deleted
            self.activeSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH)
            self.activeSubwin.installEventFilter(
                self.subWindowFilterBackground)
            self.toggle_always_on_top(self.activeSubwin, False)

    def get_other_subwindow(self):
        for subwindow in self.mdiArea.subWindowList():
            if subwindow != self.activeSubwin:
                self.otherSubwin = subwindow
                break
        self.otherSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH)
        self.columnWidth = self.otherSubwin.width()
        self.otherSubwin.installEventFilter(self.subWindowFilterBackground)
        self.toggle_always_on_top(self.otherSubwin, False)

    # window react to change in workspace size or adjust to changed size of the other
    def move_subwindows(self, checkSizeChange=True):
        # user changed size of one window in background - other has to know the right amount of space left
        def checkSizeChanges(resizer: "Resizer"):
            # fix to prevent ref window to change on workspace resize
            if resizer.mdiAreaFilter.sizeBefore[0] == resizer.mdiArea.width():
                if resizer.otherSubwin.width() != resizer.columnWidth:
                    resizer.columnWidth = resizer.otherSubwin.width()
                elif resizer.activeSubwin.width() != resizer.mdiArea.width() - resizer.columnWidth:
                    resizer.columnWidth = resizer.mdiArea.width() - resizer.activeSubwin.width()

        current = self.mdiArea.activeSubWindow()
        if current is not None:  # weird situation with maximized background window
            # two split windows
            if self.refNeeded and self.activeSubwin is not None and self.otherSubwin is not None and (not current.isMaximized()):
                if checkSizeChange == True:
                    checkSizeChanges(self)

                self._get_background_sizes()
                self.otherSubwin.move(self.otherPos)
                self.otherSubwin.resize(self.otherSize)
                self.activeSubwin.move(self.activePos)
                self.activeSubwin.resize(self.activeSize)

            if (not self.refNeeded) and self.activeSubwin is not None:  # one window on whole workspace
                self.activeSubwin.move(0, 0)
                self.activeSubwin.resize(self.mdiArea.size())

    # counting the size for newly created view
    def resize_floater(self, floater, pyFloater=None):
        if DEFAULTFLOATERSIZE is not None:  # none, means that no resizing will be done
            if pyFloater is None:  # getting python object of the same qt subwindow, if not working, needs to be taken other way and passed as argument
                self.mdiArea.setActiveSubWindow(floater)
                pyFloater = Krita.instance().activeWindow().activeView().document()

            if type(DEFAULTFLOATERSIZE) == int:  # area is given in pixels
                ratio = pyFloater.width()/pyFloater.height()
                width = int((DEFAULTFLOATERSIZE*ratio)**0.5)
                height = int(width/ratio)

            # area given as part of the whole workspace area
            if type(DEFAULTFLOATERSIZE) == float:
                allPixels = self.mdiArea.width() * self.mdiArea.height()
                spaceToGet = allPixels * DEFAULTFLOATERSIZE

                ratio = pyFloater.width()/pyFloater.height()
                width = int((spaceToGet*ratio)**0.5)
                height = int(width/ratio)

            # height given, width to be calculated
            elif DEFAULTFLOATERSIZE[0] == 0:
                height = DEFAULTFLOATERSIZE[1]
                width = pyFloater.width()/pyFloater.height() * height

            # width given, height to be calculated
            elif DEFAULTFLOATERSIZE[1] == 0:
                width = DEFAULTFLOATERSIZE[0]
                height = pyFloater.height()/pyFloater.width() * width

            else:  # fixed size given
                width = DEFAULTFLOATERSIZE[0]
                height = DEFAULTFLOATERSIZE[1]

            floater.resize(width, height + 25)

    # calculating position and size of both backgrouders
    def _get_background_sizes(self):
        if self.refPosition == "left":
            self.otherPos = QPoint(0, 0)
            self.otherSize = QSize(self.columnWidth, self.mdiArea.height())
            self.activePos = QPoint(self.columnWidth, 0)
            self.activeSize = QSize(
                int(self.mdiArea.width()-self.columnWidth), self.mdiArea.height())

        elif self.refPosition == "right":
            self.otherPos = QPoint(
                int(self.mdiArea.width()-self.columnWidth), 0)
            self.otherSize = QSize(self.columnWidth, self.mdiArea.height())
            self.activePos = QPoint(0, 0)
            self.activeSize = QSize(
                int(self.mdiArea.width()-self.columnWidth), self.mdiArea.height())

    # switch into one window mode
    def user_mode_one_window(self):
        if self.otherSubwin is not None:
            # bugfix: helps if user toggled overridden minimize button on main windows
            self.otherSubwin.showNormal()
        self.refNeeded = False

        if self.otherSubwin is not None:
            # no longer one of the two main windows
            self.otherSubwin.removeEventFilter(self.subWindowFilterBackground)
            self.otherSubwin.installEventFilter(self.subWindowFilterFloater)

            self.otherSubwin.move(0, 0)
            self.resize_floater(self.otherSubwin, None)
            self.toggle_always_on_top(self.otherSubwin, True)  # turn on
            self.otherSubwin = None

    # switch into split mode
    def user_mode_split(self):
        self.refNeeded = True
        if self.views >= 2:
            current = self.mdiArea.activeSubWindow()
            if current != self.activeSubwin:  # get a active floater to make it reference window
                if current.isMinimized():
                    current.showNormal()  # dont work!!!
                self.otherSubwin = current
                self.otherSubwin.installEventFilter(
                    self.subWindowFilterBackground)
            else:  # select random floater to make it reference window
                self.get_other_subwindow()
            self.columnWidth = self.otherSubwin.width()
            # default width for ref subwindow
            self.otherSubwin.resize(
                int(DEFAULTCOLUMNRATIO*self.mdiArea.width()), self.mdiArea.height())
            self.toggle_always_on_top(self.otherSubwin, False)

    # turn off the whole plugin
    def user_turn_off(self):
        for subwindow in self.mdiArea.subWindowList():  # remove all filters from all windows
            subwindow.removeEventFilter(self.subWindowFilterAll)
            subwindow.removeEventFilter(self.subWindowFilterFloater)
            subwindow.removeEventFilter(self.subWindowFilterBackground)

            menu = subwindow.children()[0]  # enable "always on top action"
            menu.actions()[5].setVisible(True)

        # enable default organizing actions
        if (action := Krita.instance().action('windows_cascade')) is not None:
            action.setVisible(True)
        if (action := Krita.instance().action('windows_tile')) is not None:
            action.setVisible(True)

        # disable plugin actions
        Krita.instance().action("openOverview").setVisible(False)
        Krita.instance().action("pickSubwindow").setVisible(False)

        self.activeSubwin = None
        self.otherSubwin = None

        self.user_mode_one_window()

        # filter on the workspace have to be removed that way
        if not sip.isdeleted(self.mdiAreaFilter):
            del self.mdiAreaFilter

    # turn on the whole plugin
    def user_turn_on(self):
        self.mdiAreaFilter = mdiAreaFilter(self)

        if (action := Krita.instance().action('windows_cascade')) is not None:
            action.setVisible(False)
        if (action := Krita.instance().action('windows_tile')) is not None:
            action.setVisible(False)

        self.views = len(self.mdiArea.subWindowList())

        if self.views >= 1:
            self.get_active_subwindow()
            Krita.instance().action("openOverview").setVisible(True)
        if self.views >= 2:
            Krita.instance().action("pickSubwindow").setVisible(True)

        for subwindow in self.mdiArea.subWindowList():
            subwindow.installEventFilter(self.subWindowFilterAll)
            menu = subwindow.children()[0]
            menu.actions()[5].setVisible(False)

            if subwindow.isMinimized():  # this makes sure all the windows are shown normal
                subwindow.showMaximized()
            if subwindow.isMaximized():
                subwindow.showNormal()

            if subwindow != self.activeSubwin:
                subwindow.installEventFilter(self.subWindowFilterFloater)
                self.toggle_always_on_top(subwindow, True)
                self.resize_floater(subwindow)

        if self.views >= 1:
            self.move_subwindows()

    def switch_background_windows(self):
        self.otherSubwin.resize(self.activeSubwin.size())

        temp = self.otherSubwin
        self.otherSubwin = self.activeSubwin
        self.activeSubwin = temp

        self.mdiArea.setActiveSubWindow(self.activeSubwin)

    # opens grayscale overwiev
    def user_open_overview(self):
        self.mdiArea.setActiveSubWindow(self.activeSubwin)
        doc = Krita.instance().activeDocument()
        Krita.instance().activeWindow().addView(doc)
        if SOFTPROOFING:
            Krita.instance().action("softProof").trigger()
        overview = self.mdiArea.subWindowList()[-1]
        overview.move(self.mdiArea.width() - overview.width(),
                      self.mdiArea.height() - overview.height())

    def switch_background_and_floater(self, background, floater):
        if floater.isMinimized():
            floater.showNormal()
        floaterPos = copy(floater.pos())  # resize and move both
        floaterSize = copy(floater.size())

        floater.removeEventFilter(self.subWindowFilterFloater)
        floater.installEventFilter(self.subWindowFilterBackground)
        self.toggle_always_on_top(floater, False)

        if background == self.activeSubwin:  # the only way it works well
            floater.move(self.activeSubwin.pos())
            floater.resize(self.activeSubwin.size())
            temp = self.activeSubwin
            self.activeSubwin = floater

        else:  # background == self.otherSubwin
            floater.move(self.otherSubwin.pos())
            floater.resize(self.otherSubwin.size())
            temp = self.otherSubwin
            self.otherSubwin = floater

        self.mdiArea.setActiveSubWindow(temp)

        temp.removeEventFilter(self.subWindowFilterBackground)
        temp.installEventFilter(self.subWindowFilterFloater)

        temp.resize(floaterSize)
        temp.move(floaterPos)
        self.toggle_always_on_top(temp, True)

    # swapping subwindows with the keyboard/menu action instead of drag and drop
    def user_toggle_subwindow(self):

        # those help if user toggled overridden minimize button on main windows
        self.activeSubwin.showNormal()
        if self.otherSubwin is not None:
            self.otherSubwin.showNormal()

        current = self.mdiArea.activeSubWindow()
        if self.refNeeded:
            # switch two main windows
            if (current == self.activeSubwin or current == self.otherSubwin) and self.otherSubwin is not None:
                self.switch_background_windows()

            # set floater as ref
            elif current != self.activeSubwin and current != self.otherSubwin:
                self.switch_background_and_floater(self.otherSubwin, current)
        else:  # one window mode
            if current != self.activeSubwin:
                self.switch_background_and_floater(self.activeSubwin, current)

        self.move_subwindows()
