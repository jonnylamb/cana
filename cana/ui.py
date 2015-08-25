from gi.repository import Gtk, Gdk

import random

class BaseWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        self.connect('key-press-event', self.key_press_event)

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

        self.score = Gtk.Label('')
        self.vbox.pack_end(self.score, False, False, 0)
        self.score.show()

    def activated(self, window, data):
        raise NotImplementedError

    def key_press_event(self, window, event):
        if (event.state & Gdk.ModifierType.CONTROL_MASK \
            and event.keyval == Gdk.KEY_q) or \
            event.keyval == Gdk.KEY_Escape:
            # block starts here
            window.destroy()

class VerbWindow(BaseWindow):
    english_names = ['i', 'you', 'she', 'we', 'you (pl)', 'they']

    def __init__(self, verbs):
        BaseWindow.__init__(self)

        self.verbs = verbs

        entry = Gtk.Entry()
        entry.set_activates_default(True)
        self.entrybox.add(entry)
        entry.show()

        self.random_iter = []
        self.score_count = [0, 0]

        self.next()

    def random(self):
        if not self.random_iter:
            self.random_iter = self.verbs[:]
            random.shuffle(self.random_iter)

        return self.random_iter.pop()

    @property
    def entry(self):
        children = self.entrybox.get_children()
        assert len(children) == 1, children

        return children[0]

    @property
    def complete(self):
        return self.entry.get_text() != ''

    def update_score(self):
        if self.question.get_text() is not '':
            passed = not self.correction.get_visible()

            if passed:
                self.score_count[0] += 1
            self.score_count[1] += 1

        self.score.set_text('%s/%s' % (self.score_count[0], self.score_count[1]))

    def next(self):
        self.update_score()

        # clear up first
        self.question.set_text('')
        self.correction.hide()
        self.entry.set_text('')

        verb = self.random()
        mood = verb.random()
        tense = mood.random()
        self.iter = tense.random()

        num, display, answers = self.iter

        if display == ' ': # I don't like this any more than you
            english_name = self.english_names[num]

            display = '%s %s\n%s\n<i>%s</i>' % (mood.name, tense.name, english_name, verb.english_name)

        self.question.set_markup('<span font="Sans 60">%s</span>' % display)
        self.entry.grab_focus()

    def check(self):
        num, display, answers = self.iter
        if self.entry.get_text().lower() in answers:
            return True

        # use -1 index because the assumption is the most complete
        # form is the last in the tuple. for example, in italian it
        # will be ('mangio', 'io mangio')
        correction = '<span font="Sans 60" foreground="red">%s</span>' % answers[-1]

        self.correction.set_markup(correction)
        self.correction.show()

        self.entry.set_text('')
        self.entry.grab_focus()
        return False

    def activated(self, window, data):

        # is it complete?
        if not self.complete:
            return

        if not self.check():
            return

        try:
            self.next()
        except IndexError:
            # TODO end
            self.question.set_markup('<span font="Sans Italic 60">fin</span>')
            pass
