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
        if date is None:
            date = datetime(1970, 1, 1)

        ret = []

        groups, _ = self.keyfile.get_groups()
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

        return self.random_iter.pop()

class Mood(object):
    def __init__(self, name):
        self.name = name
        self.tenses = []

    def add(self, tense):
        self.tenses.append(tense)

    def random(self):
        return random.choice(self.tenses)

class Verb(object):
    def __init__(self, name):
        self.name = name

        self.keyfile = GLib.KeyFile.new()
        self.keyfile.load_from_file('verbs/' + self.name,
                                    GLib.KeyFileFlags.KEEP_COMMENTS)

        self.indicative = self.parse_conjugation('indicative',
                                                 ['present', 'imperfect', 'future'])
        self.random_iter = []

    def random(self):
        if not self.random_iter:
            self.random_iter = [self.indicative]
            random.shuffle(self.random_iter)

        return self.random_iter.pop()

    def parse_conjugation(self, mood, tenses):
        t = []
        m = Mood(mood)

        for tense in tenses:
            conj_it, _ = self.keyfile.get_string_list(mood, tense + '-it')

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

            it = zip(personal_it, conj_it)
            en = zip(personal_en, conj_en)

            m.add(Tense(tense, it, en))

        return m

    @property
    def english_name(self):
        return self.keyfile.get_string('misc', 'en')

    @property
    def auxiliary(self):
        return self.keyfile.get_string('misc', 'auxiliary')

    @property
    def gerund(self):
        return self.keyfile.get_string('misc', 'gerund')

    @property
    def past_m(self):
        return self.keyfile.get_string('misc', 'past-m')

    @property
    def past_f(self):
        return self.keyfile.get_string('misc', 'past-f')
