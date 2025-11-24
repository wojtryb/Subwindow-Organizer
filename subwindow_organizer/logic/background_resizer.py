from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow


class BackgroundResizer:
    def __init__(self, mdi_area: QMdiArea) -> None:
        self.mdi_area = mdi_area
        self.left: QMdiSubWindow | None = None
        self.right: QMdiSubWindow | None = None

    def add(self, subwindow: QMdiSubWindow):
        if self.left is None:
            self.left = subwindow
        elif self.right is None:
            self.right = subwindow

    def remove(self, subwindow: QMdiSubWindow):
        if self.right == subwindow:
            self.right = None
        elif self.left == subwindow:
            self.left = self.right
            self.right = None

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

    def __contains__(self, value):
        if not isinstance(value, QMdiSubWindow):
            return False
        return value == self.left or value == self.right
