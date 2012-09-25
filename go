#!/usr/bin/env python

import sys

from gi.repository import Gtk

from cana.data import Data
from cana.ui import TestWindow
from cana.app import Application

if __name__ == '__main__':
    data = Data('test')

    app = Application()

    window = TestWindow(data.italian())
    app.add_window(window)
    window.show()

    app.run(sys.argv)
