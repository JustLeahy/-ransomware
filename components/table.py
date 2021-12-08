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
        return cls.MAPPING[ch] if cls.MAPPING.has