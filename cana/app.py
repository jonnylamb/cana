from gi.repository import Gtk, Gio

class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id='com.jonnylamb.Cana',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.connect('activate', lambda a,b: None, None)
