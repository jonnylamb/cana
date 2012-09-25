from datetime import datetime

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
