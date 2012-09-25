from gi.repository import Gtk

class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

        self.connect('activate', lambda a,b: None, None)
