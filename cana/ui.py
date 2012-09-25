from gi.repository import Gtk

import random

class TestWindow(Gtk.Window):
    def __init__(self, data):
        Gtk.Window.__init__(self)

        self.data = data
        self.keys = data.keys()
        random.shuffle(self.keys)

        self.vbox = Gtk.VBox(False, 5)
        self.add(self.vbox)
        self.vbox.show()

        self.question = Gtk.Label('')
        self.vbox.add(self.question)
        self.question.show()

        self.correction = Gtk.Label('')
        self.vbox.add(self.correction)

        self.entrybox = Gtk.VBox(False, 0)
        self.vbox.add(self.entrybox)
        self.entrybox.show()

        self.nextbutton = Gtk.Button('Next')
        self.nextbutton.set_can_default(True)
        self.nextbutton.connect('activate', self.activated, None)

        self.set_default(self.nextbutton)

        self.next()

    def next(self):
        # clear up first
        self.question.set_text('')
        self.correction.hide()
        self.entrybox.foreach(lambda w, c: c.remove(w), self.entrybox)

        self.iter = self.keys.pop()
        values = self.data[self.iter]

        self.question.set_markup('<span font="Sans 60">%s</span>' % self.iter)

        for val in values:
            entry = Gtk.Entry()
            entry.set_activates_default(True)
            self.entrybox.add(entry)
            entry.show()

        self.give_focus()

    def give_focus(self):
        # returns True if all entries have something, otherwise Fals
        # go in reverse so we don't select all the completed entries
        children = self.entrybox.get_children()
        children.reverse()

        ret = True

        for entry in children:
            if entry.get_text() == '':
                entry.grab_focus()
                ret = False

        return ret

    def check(self):
        res = True
        values = self.data[self.iter]

        for entry in self.entrybox.get_children():
            tmp = entry.get_text()
            entry.set_text('')

            if tmp in values:
                values.remove(tmp)
            else:
                res = False

        if not res:
            values = self.data[self.iter]
            values_markup = ['<span font="Sans 60" foreground="red">%s</span>' % x for x in values]

            self.correction.set_markup('\n'.join(values_markup))
            self.correction.show()

            self.give_focus()

        return res

    def activated(self, shrug, data):

        # is it complete?
        if not self.give_focus():
            return

        if not self.check():
            return

        try:
            self.next()
        except IndexError:
            # TODO end
            self.question.set_markup('<span font="Sans Italic 60">fin</span>')
            pass

