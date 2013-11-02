__author__ = 'thomaswatson'
from cStringIO import StringIO


class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = StringIO()

    def Append(self, str):
        self._file_str.write(str)

    def AppendLine(self, str):
        self._file_str.write("{0}\n".format(str))

    def __str__(self):
        return self._file_str.getvalue()