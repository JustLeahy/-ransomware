"""A class to store tables.

Sample Usage:
    table = SgTable()
    table.Append([1, 2, 3])
    table.Append([2, 4, 6])
    table.Append([3, 6, 9])
    for row in table:
        print(row)
    print(table[1])
    table[1] = [2, 2, 2]
    print(table[1])
    table.SetFields(["a", "b", "c"])
    print(table.GetVals("a"))
    print(table.GetVals("b"))
    print(table.GetVals("c"))
    print(table[1:])
    print(table[:2])
    print(table[0:2:2])
"""

import itertools


class EscapeHtml:
    MAPPING = {u"&": u"&amp;",
               u"<": u"&lt;",
               u">": u"&gt;",
               u"\"": u"&quot;",
               u"\'": u"&#39;",
               u"\n": u"<br>\n"}

    @classmethod
    def Escape(cls, ch):
        return cls.MAPPING[ch] if cls.MAPPING.has_key(ch) else ch

    @classmethod
    def EscapeUnicodeStr(cls, unicode_str):
        ret = u""
        for ch in unicode_str:
            ret += cls.Escape(ch)
        return ret


class SgTable:
    """A class to store tables."""

    def __init__(self):
        self._fields = []
        self._table = []

    def __len__(self):
        return len(self._table)

    def __iter__(self):
        for row in self._table:
            yield row

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self._table[key.start:key.stop:key.step]
        else:
            if not ((type(key) == int or type(key) == long) and key >= 0 and key < len(self._table)):
                raise ValueError("Index illegal")
            else:
                return self._table[key]

    def __setitem__(self, key, value):
        if not ((type(key) == int or type(key) == long) and key >= 0 and key < len(self._table)):
            raise ValueError("Index illegal")
        else:
            self._table[key] = value

    def __str__(self):
        ret = str(self._fields)
        for row in self._table:
            ret += "\n" + str(row)
        return ret

    def __HasCommaOutOfString(self, val):
        in_string = False
        is_escaping = False
        for ch in val:
            if in_string:
                if is_escaping:
                    is_escaping = False
                elif ch == u"\\":
                    is_escaping = True
                elif ch in (u"\"", u"\'"):
                    in_string = False
            else:
                if ch == 