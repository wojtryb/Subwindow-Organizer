from krita import Krita

"""
The only python file directly run by krita during plugin init phase.

Checks whether plugin requirements are met and aborts the start if not.
"""
import sys
import os

# Appending this file location to python PATH allows to directly import
# main packages instead of using relative imports.
sys.path.append(directory := os.path.dirname(__file__))

from .subwindow_organizer import SubwindowOrganizer  # noqa

Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
