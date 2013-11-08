__author__ = 'thomaswatson'
from cStringIO import StringIO

class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = StringIO()

    def append(self, str):
        self._file_str.write(str)

    def appendLine(self, str):
        self._file_str.write("{0}\n".format(str))

    def __str__(self):
        return self._file_str.getvalue()


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
