from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow


class BackgroundResizer:
    def __init__(self, mdi_area: QMdiArea) -> None:
        self.mdi_area = mdi_area
        self.left: QMdiSubWindow | None = None
        self.right: QMdiSubWindow | None = None

    def add(self, subwindow: QMdiSubWindow):
        if self.left is None:
            self.left = subwindow
            self.resize_background_subwindows()
        elif self.right is None:
            self.right = subwindow
            self.resize_background_subwindows()

    def remove(self, subwindow: QMdiSubWindow):
        if self.right == subwindow:
            self.right = None
            self.resize_background_subwindows()
        elif self.left == subwindow:
            self.left = self.right
            self.right = None
            self.resize_background_subwindows()

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
