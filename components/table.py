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
                if ch == u",":
                    return True
                elif ch in (u"\"", u"\'"):
                    in_string = True
        return False

    def _GetCsvRepr(self, val):
        if isinstance(val, list):
            return u",".join(itertools.imap(self._GetCsvRepr, val))
        else:
            if isinstance(val, unicode):
                if self.__HasCommaOutOfString(val) or u"\n" in val:
                    return u"\"" + val + u"\""
                else:
                    return val
            else:
                return unicode(str(val), "utf-8")

    def InCsv(self):
        ret = self._GetCsvRepr(self._fields)
        for row in self._table:
            ret += u"\n" + self._GetCsvRepr(row)
        return ret

    def InHtml(self):
        ret = u"<html>\n<head><meta charset=\"utf-8\">\n<title>SQLGitHub Result</title>\n</head>\n<body>\n"

        ret += u"<table border=1>"
        ret += u"<tr>"
        for field in self._fields:
            ret += u"<td>" + EscapeHtml.EscapeUnicodeStr(field) + u"</td>"
        ret += u"</tr>\n"
        for row in self._table:
            ret += u"<tr>"
            for val in row:
                unicode_str = val if isinstance(val, unicode) else unicode(str(val), "utf-8")
                ret += u"<td>" + EscapeHtml.EscapeUnicodeStr(unicode_str) + u"</td>"
            ret += u"</tr>\n"
        ret += u"</table>\n</html>"
        return ret

    def GetVals(self, field):
        idx = [i for i, f in enumerate(self._fields) if f == field][0]
        return [row[idx] for row in self._table]

    def Copy(self, table):
        self.SetFields(table.GetFields())
        self.SetTable(table.GetTable())
    
    def Append(self, row):
        self._table.append(row)

    def GetTable(self):
        return self._table

    def SetTable(self, table):
        self._table = table

    def GetFields(self):
        return self._fields

    def SetFields(self, fields):
        self._fields = fields
    
    def SliceCol(self, start, end):
        table = SgTable()
        table.SetFiel