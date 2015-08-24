# -*- coding: utf-8 -*-
from datetime import datetime
import random

from gi.repository import GLib

class Data(object):
    def __init__(self, filename):
        self.filename = filename

        self.keyfile = GLib.KeyFile.new()
        self.keyfile.load_from_file(self.filename,
                                    GLib.KeyFileFlags.KEEP_COMMENTS)

    def dates(self, date):
        ret = []

        groups, _ = self.keyfile.get_groups()

        if date is None:
            return groups

        for group in groups:
            groupdate = datetime.strptime(group, '%Y-%m-%d')

            if groupdate >= date:
                ret.append(group)

        return ret

    def italian(self, date=None):
        groups = self.dates(date)

        ret = {}

        for group in groups:
            keys, _ = self.keyfile.get_keys(group)

            for key in keys:
                vals, _x = self.keyfile.get_string_list(group, key)

                ret[key] = vals

        return ret

class Tense(object):
    def __init__(self, name, it, en):
        self.name = name
        self.it = it # [('io', 'sono'), ('tu', 'sei'), ...]
        self.en = en # [('i', 'am'), ...]

        self.random_iter = []

    def italian(self):
        # of form: (0, 'i am', ('io sono', 'sono'))

        if not self.random_iter:
            self.random_iter = zip(range(6),
                                   [' '.join(x) for x in self.en],
                                   [(x[-1], ' '.join(x)) for x in self.it])
            random.shuffle(self.random_iter)

        if self.random_iter[0] == 0 and self.random_iter[1] == 'i ':
            # imperative first person singular
            self.random_iter.pop()
            return self.italian()

        return self.random_iter.pop()

class Mood(object):
    def __init__(self, name):
        self.name = name
        self.tenses = []

        self.random_iter = []

    def add(self, tense):
        self.tenses.append(tense)

    def random(self):
        if not self.random_iter:
            self.random_iter = self.tenses[:]
            random.shuffle(self.random_iter)

        return self.random_iter.pop()

class Verb(object):
    def __init__(self, name):
        self.name = name

        self.keyfile = GLib.KeyFile.new()
        self.keyfile.load_from_file('verbs/' + self.name,
                                    GLib.KeyFileFlags.KEEP_COMMENTS)

        self.indicative = self.parse_conjugation('indicative',
                                                 ['present', 'imperfect', 'future'])
        self.conditional = self.parse_conjugation('conditional', ['present'])
        if not self.skip_past:
            self.do_simple_past(self.indicative)
        if not self.skip_gerund:
            self.do_gerund(self.indicative)

        # ignore this for now
        #self.imperative = self.parse_conjugation('imperative', ['present'])

        self.random_iter = []

    def random(self):
        if not self.random_iter:
            self.random_iter = [self.indicative, self.conditional]
            random.shuffle(self.random_iter)

        return self.random_iter.pop()

    def parse_conjugation(self, mood, tenses):
        t = []
        m = Mood(mood)

        for tense in tenses:
            try:
                conj_it, _ = self.keyfile.get_string_list(mood, tense + '-it')
            except:
                continue

            try:
                conj_en, _ = self.keyfile.get_string_list(mood, tense + '-en')
                personal_en = ['i', 'you', 'she', 'we', 'you (pl)', 'they']
            except:
                # english doesn't exist, no wuckers
                conj_en = personal_en = [''] * 6

            personal_it = ['io', 'tu', 'lei', 'noi', 'voi', 'loro']
            if mood == 'subjunctive':
                personal_it = ['che io', 'che tu', 'che lei', 'che noi', 'che voi', 'che loro']
            elif mood == 'imperative':
                personal_it[0] = ''
            elif mood == 'conditional' and conj_en == personal_en: # empty translation
                personal_en = ['i would', 'you would', 'she would', 'we would', 'you (pl) would', 'they would']
                conj_en = [self.english_name.split(' ')[-1]] * 6

            it = zip(personal_it, conj_it)
            en = zip(personal_en, conj_en)

            # it = [('io', 'ho mangiato'), ('tu', 'hai mangiato'), ...]
            # (ignoring that that's past)
            m.add(Tense(tense, it, en))

        return m

    def do_simple_past(self, mood):
        personal_it = ['io', 'tu', 'lei', 'noi', 'voi', 'loro']
        personal_en = ['i', 'you', 'she', 'we', 'you (pl)', 'they']

        if self.auxiliary == 'essere':
            aux = ['sono', 'sei', 'è', 'siamo', 'siete', 'sono']

            # we really need this to be true for anything to make sense
            assert self.past_m[-1] == 'o', self.past_m

            try:
                tps_past = self.past_f
            except:
                tps_past = self.past_m[:-1] + 'a'

            p_past = self.past_m[:-1] + 'i'

        elif self.auxiliary == 'avere':
            aux = ['ho', 'hai', 'ha', 'abbiamo', 'avete', 'hanno']
            tps_past = self.past_m
            p_past = self.past_m
        else:
            raise Exception('unknown auxiliary: %s' % self.auxiliary)

        pasts = [self.past_m] * 2 + [tps_past] + [p_past] * 3

        # [('io', 'ho mangiato'), ('tu', 'hai mangiato'), ...]
        it = [(personal_it[x], '%s %s' % (aux[x], pasts[x])) for x in range(6)]

        try:
            en = [(personal_en[x], self.past_en) for x in range(6)]
        except:
            empty = [''] * 6
            en = zip(empty, empty)

        mood.add(Tense('simple past', it, en))

    def do_gerund(self, mood):
        personal_it = ['io', 'tu', 'lei', 'noi', 'voi', 'loro']
        it_stare = ['sto', 'stai', 'sta', 'stiamo', 'state', 'stanno']
        en_be = ['i am', 'you are', 'she is', 'we are', 'you (pl) are', 'they are']

        # [('io', 'sto mangiando'), ('tu', 'stai mangiando'), ...]
        it = [(personal_it[x], '%s %s' % (it_stare[x], self.gerund)) for x in range(6)]

        # [('i am', 'eating'), ...]
        en = [(en_be[x], self.gerund_en) for x in range(6)]

        mood.add(Tense('gerund', it, en))

    @property
    def english_name(self):
        return self.keyfile.get_string('misc', 'en')

    @property
    def skip_past(self):
        try:
            return not bool(self.past_m)
        except:
            return True

    @property
    def skip_gerund(self):
        try:
            return not bool(self.gerund)
        except:
            return True

    @property
    def auxiliary(self):
        return self.keyfile.get_string('misc', 'auxiliary')

    @property
    def gerund(self):
        return self.keyfile.get_string('misc', 'gerund')

    @property
    def gerund_en(self):
        return self.keyfile.get_string('misc', 'gerund-en')

    @property
    def past_m(self):
        return self.keyfile.get_string('misc', 'past-m')

    @property
    def past_f(self):
        return self.keyfile.get_string('misc', 'past-f')

    @property
    def past_en(self):
        return self.keyfile.get_string('misc', 'past-en')
