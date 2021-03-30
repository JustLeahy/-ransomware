
"""A set of utility functions to evaluate expressions.

Sample Usage:
    print(SgExpression.ExtractTokensFromExpression("name + issues_url"))
    print(SgExpression.ExtractTokensFromExpressions(["name + issues_url", "issues_url - id"]))
    print(SgExpression.IsAllTokensInAggregate(["avg(mycount + 5)", "max(5 + min(yo))"]))
    print(SgExpression.IsAllTokensInAggregate(["avg(mycount + 5) + secondcount", "max(5 + min(yo))"]))
    table = tb.SgTable()
    table.SetFields([u"a", u"b", u"a_b", u"c"])
    table.Append([1, 2, 3, u"A"])
    table.Append([2, 4, 6, u"BB"])
    table.Append([3, 6, 9, u"CCC"])
    table.Append([4, 8, 12, u"ABC"])
    print(SgExpression.EvaluateExpression(table, u"a * (b - a_b)"))
    print(SgExpression.EvaluateExpression(table, u"MIN(a * (b - a_b))"))
    print(SgExpression.EvaluateExpression(table, u"MAX(a * (b - a_b))"))
    print(SgExpression.EvaluateExpression(table, u"-7 + a*(b-a_b)"))
    print(SgExpression.EvaluateExpression(table, u"max(a*(b-a_b))"))
    print("---")
    print(SgExpression.EvaluateExpression(table, u"a * b - a_b + a_b % a"))
    print(SgExpression.EvaluateExpression(table, u"MIN(a * b - a_b + a_b % a)"))
    print(SgExpression.EvaluateExpression(table, u"MAX(a * b - a_b + a_b % a)"))
    print(SgExpression.EvaluateExpression(table, u"a*b-a_b+a_b%a"))
    print(SgExpression.EvaluateExpression(table, u"max(a*b-a_b+a_b%a)"))
    print("---")
    print(SgExpression.EvaluateExpression(table, u"3 + 2 = 5"))
    print(SgExpression.EvaluateExpression(table, u"6 = 3 + 2"))
    print(SgExpression.EvaluateExpression(table, u"a_b * a_b - b > 10"))
    print(SgExpression.EvaluateExpression(table, u"\"aaa\" is \"aaa\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"%\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"%A\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"C_C\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"A\""))
    print(SgExpression.EvaluateExpression(table, "\"%%%\" like \"\\%_\\%\""))
    print(SgExpression.EvaluateExpression(table, "\"a%%\" like \"\\%_\\%\""))
    print(SgExpression.EvaluateExpression(table, "\"%a%\" like \"\\%_\\%\""))
    print(SgExpression.EvaluateExpression(table, u"c regexp \"B*\""))
    print(SgExpression.EvaluateExpression(table, u"c regexp \"[B-C]*\""))
    print(SgExpression.EvaluateExpression(table, u"\"BB\" in (\"A\", \"B\", c)"))
    print("---")
    print(SgExpression.EvaluateExpression(table, "not a + 2 >= b"))
    print(SgExpression.EvaluateExpression(table, "not a + 2 >= b and a_b > 10"))
    print(SgExpression.EvaluateExpression(table, "b < 5 || a_b > 10"))
    print("---")
    print(SgExpression.EvaluateExpression(table, "sum(a + b)"))
    print(SgExpression.EvaluateExpression(table, "avg(a * a)"))
    print(SgExpression.EvaluateExpression(table, u"CONCAT(\"a\", c, \"ccc\", -7 + 8)"))
"""

import re
import regex  # need recursive pattern

import definition as df
import utilities as util
import table as tb
import math
import datetime

class SgExpression:
    """A set of utility functions to evaluate expressions."""
