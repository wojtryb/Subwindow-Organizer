from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow


class Resizer:

    def __init__(self, mdi_area: QMdiArea):
        self.mdi_area = mdi_area

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
