from gi.repository import Gtk

import random

class BaseWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

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

    def activated(self, shrug, data):
        raise NotImplementedErrr

class TestWindow(BaseWindow):
    def __init__(self, data):
        BaseWindow.__init__(self)

        self.data = data
        self.keys = data.keys()
        random.shuffle(self.keys)

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
        values = self.data[self.iter][:]

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
        self.iter = tense.italian()

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

        correction = '<span font="Sans 60" foreground="red">%s</span>' % answers[1]

        self.correction.set_markup(correction)
        self.correction.show()

        self.entry.set_text('')
        self.entry.grab_focus()
        return False

    def activated(self, shrug, data):

        # is it complete?
        if not self.complete():
            return

        if not self.check():
            return

        try:
            self.next()
        except IndexError:
            # TODO end
            self.question.set_markup('<span font="Sans Italic 60">fin</span>')
            pass

