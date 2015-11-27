from gi.repository import Gtk, Gio

class Application(Gtk.Application):
    def __init__(self, args):
        Gtk.Application.__init__(self, application_id='com.jonnylamb.Cana',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.args = args
