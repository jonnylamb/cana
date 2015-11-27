# -*- coding: utf-8 -*-
import random

from gi.repository import GLib

class Tense(object):
    def __init__(self, name, foreign, en, require_personal=False, special=None):
        self.name = name
        self.foreign = foreign # [('io', 'sono'), ('tu', 'sei'), ...]
        self.en = en # [('i', 'am'), ...]
        self.require_personal = require_personal

        if special:
            self.special = special
        else:
            self.special = lambda s: s

        self.random_iter = []

    def __str__(self):
        return '<Tense: %s>' % self.name

    def answers(self):
        if self.require_personal:
            return [tuple([self.special(' '.join(x))]) for x in self.foreign]
        else:
            return [(x[-1], self.special(' '.join(x))) for x in self.foreign]

    def random(self):
        # returns form: (0, 'i am', ('io sono', 'sono'))
        # where (id, english, (possible, answers))

        if not self.random_iter:
            self.random_iter = zip(range(6),
                                   [' '.join(x) for x in self.en],
                                   self.answers())
            random.shuffle(self.random_iter)

        return self.random_iter.pop()

class Mood(object):
    def __init__(self, name):
        self.name = name
        self.tenses = []

        self.random_iter = []

    def __str__(self):
        return '<Mood: %s>' % self.name

    def add(self, tense):
        self.tenses.append(tense)

    def random(self):
        if not self.random_iter:
            self.random_iter = self.tenses[:]
            random.shuffle(self.random_iter)

        return self.random_iter.pop()

    def has_tenses(self):
        return bool(self.tenses)

class Verb(object):
    def __init__(self, name, keyfile=None):
        self.name = name

        self.keyfile = keyfile
        if not self.keyfile:
            self.keyfile = GLib.KeyFile.new()
            self.keyfile.load_from_file('verbs/' + self.name,
                                        GLib.KeyFileFlags.KEEP_COMMENTS)

        self.moods = []
        self.random_iter = []

    def __str__(self):
        return '<Verb: %s>' % self.name

    def random(self):
        if not self.random_iter:
            self.random_iter = []
            for i in self.moods:
                if i.has_tenses():
                    self.random_iter.append(i)

            random.shuffle(self.random_iter)

        return self.random_iter.pop()

    def parse_conjugation(self, mood, tenses):
        t = []
        m = Mood(mood)

        for tense in tenses:
            try:
                conj_foreign = self.keyfile.get_string_list(mood, tense + '-' + self.SUFFIX)
            except Exception as e:
                print 'problem parsing %s %s: %s' % (mood, tense, e)
                continue

            try:
                conj_en = self.keyfile.get_string_list(mood, tense + '-en')
                personal_en = ['i', 'you', 'she', 'we', 'you (pl)', 'they (f)']
            except Exception as e:
                # english doesn't exist, no wuckers
                conj_en = personal_en = [''] * 6

            personal_foreign = self.PERSONAL_INDICATIVE
            if mood == 'subjunctive':
                personal_foreign = self.PERSONAL_SUBJUNCTIVE
            elif mood == 'imperative':
                personal_foreign[0] = ''
            elif mood == 'conditional' and conj_en == personal_en: # empty translation
                personal_en = ['i would', 'you would', 'she would', 'we would', 'you (pl) would', 'they would']
                # if the verb is "to dance it off", use "dance it off"
                conj_en = [' '.join(self.english_name.split(' ')[1:])] * 6

            foreign = zip(personal_foreign, conj_foreign)
            en = zip(personal_en, conj_en)

            # foreign = [('io', 'mangio'), ('tu', 'mangi'), ...]

            # have to set require_personal and special because this is
            # the base class
            m.add(Tense(tense, foreign, en,
                        require_personal=self.REQUIRE_PERSONAL_PRONOUN,
                        special=self.special))

        return m

    def special(self, answer):
        return answer

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

class ItalianVerb(Verb):
    SUFFIX = 'it'
    PERSONAL_INDICATIVE = ['io', 'tu', 'lei', 'noi', 'voi', 'loro']
    PERSONAL_SUBJUNCTIVE = ['che ' + s for s in PERSONAL_INDICATIVE]
    REQUIRE_PERSONAL_PRONOUN = False

    def __init__(self, name, keyfile=None):
        Verb.__init__(self, name, keyfile)

        self.indicative = self.parse_conjugation('indicative',
                                                 ['present', 'imperfect', 'future'])
        self.conditional = self.parse_conjugation('conditional', ['present'])
        if not self.skip_past:
            self.do_simple_past(self.indicative)
        if not self.skip_gerund:
            self.do_gerund(self.indicative)

        # ignore this for now
        #self.imperative = self.parse_conjugation('imperative', ['present'])

        self.subjunctive = self.parse_conjugation('subjunctive', ['present', 'imperfect'])

        self.moods = [self.indicative, self.conditional, self.subjunctive]

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

class FrenchVerb(Verb):
    SUFFIX = 'fr'
    PERSONAL_INDICATIVE = ['je', 'tu', 'elle', 'nous', 'vous', 'elles']
    PERSONAL_SUBJUNCTIVE = ['que je', 'que tu', 'qu\'elle', 'que nous', 'que vous', 'qu\'elles']
    REQUIRE_PERSONAL_PRONOUN = True

    def __init__(self, name, keyfile=None):
        Verb.__init__(self, name, keyfile)

        self.indicative = self.parse_conjugation('indicative',
                                                 ['present', 'imperfect', 'future'])
        self.conditional = self.parse_conjugation('conditional', ['present'])
        if not self.skip_past:
            self.do_passe_compose(self.indicative)

        # ignore this for now
        #self.imperative = self.parse_conjugation('imperative', ['present'])

        self.subjunctive = self.parse_conjugation('subjunctive', ['present', 'imperfect'])

        self.moods = [self.indicative, self.conditional, self.subjunctive]

    def do_passe_compose(self, mood):
        personal_fr = ['je', 'tu', 'elle', 'nous', 'vous', 'elles']
        personal_en = ['i', 'you', 'she', 'we', 'you (pl)', 'they (f)']

        if self.auxiliary == 'être':
            aux = ['suis', 'es', 'est', 'sommes', 'êtes', 'sont']
            fem_past = self.past_m + 'e'
            plural_suffix = 's'
        elif self.auxiliary == 'avoir':
            aux = ['hai', 'as', 'a', 'avons', 'avez', 'ont']
            fem_past = self.past_m
            plural_suffix = ''
        else:
            raise Exception('unknown auxiliary: %s' % self.auxiliary)

        pasts = [self.past_m] * 2 + [fem_past] + [self.past_m + plural_suffix] * 2 + [fem_past + plural_suffix]

        # [('je', 'hai mangé'), ('tu', 'as mangé'), ...]
        fr = [(personal_fr[x], '%s %s' % (aux[x], pasts[x])) for x in range(6)]

        try:
            en = [(personal_en[x], self.past_en) for x in range(6)]
        except:
            empty = [''] * 6
            en = zip(empty, empty)

        mood.add(Tense('passé composé', fr, en,
                       require_personal=True,
                       special=self.special))

    def special(self, answer):
        if answer.startswith('je hai'):
            return 'j\'hai' + answer[len('je hai'):]

        return answer

def parse(name):
    keyfile = GLib.KeyFile.new()

    try:
        keyfile.load_from_file('verbs/' + name,
                               GLib.KeyFileFlags.KEEP_COMMENTS)

        aux = keyfile.get_string('misc', 'auxiliary')
    except Exception as e:
        print 'failed to parse verb "%s": %s' % (name, e)
        return None

    if aux in ('essere', 'avere'):
        return ItalianVerb(name, keyfile=keyfile)
    elif aux in ('être', 'etre', 'avoir'):
        return FrenchVerb(name, keyfile=keyfile)
    else:
        raise Exception('invalid auxiliary "%s" for verb "%s"' % (aux, name))

    return None
