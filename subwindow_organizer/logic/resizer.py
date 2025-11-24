from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow
from PyQt5.QtCore import QSize


class Resizer:

    def __init__(self, mdi_area: QMdiArea):
        self.mdi_area = mdi_area
        self.left: QMdiSubWindow | None = None
        self.right: QMdiSubWindow | None = None

    # snapping floaters to border of the canvas
    def snap_to_border(self, subwindow: QMdiSubWindow):
        SNAPDISTANCE = 30

        x = subwindow.pos().x()
        y = subwindow.pos().y()

        if x < SNAPDISTANCE:
            x = 0
        if y < SNAPDISTANCE:
            y = 0
        if x + subwindow.width() > self.mdi_area.width() - SNAPDISTANCE:
            x = self.mdi_area.width() - subwindow.width()
        if y + subwindow.height() > self.mdi_area.height() - SNAPDISTANCE:
            y = self.mdi_area.height() - subwindow.height()

        subwindow.move(x, y)

    def resize_to_suggested_size(self, subwindow: QMdiSubWindow):
        SUGGESTED_SIZE = QSize(400, 500)
        subwindow.resize(SUGGESTED_SIZE)

    # def swap_subwindows(self, a: QMdiSubWindow, b: QMdiSubWindow):
    #     a_pos = a.pos()
    #     b_pos = b.pos()
    #     a_size = a.size()
    #     b_size = b.size()

    #     a.resize(b_size)
    #     a.move(b_pos)
    #     b.resize(a_size)
    #     b.move(a_pos)

    def resize_background_subwindows(self):
        if self.left is not None and self.right is None:
            self.left.resize(self.mdi_area.size())
            self.left.move(0, 0)
        if self.left is not None and self.right is not None:
            width, height = self.mdi_area.width(), self.mdi_area.height()

            self.left.resize(round(width * 0.5), height)
            self.left.move(0, 0)
            self.right.resize(round(width * 0.5), height)
            self.right.move(width, 0)
