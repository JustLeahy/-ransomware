
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

    # (?:something) means a non-capturing group
    # Matches anything word that isn't postfixed with a '(' (not a function name)
    # Adding a non-alpha character as matching postfix to prevent cases like 'www(' having a match 'ww'
    _TOKEN_BODY = r"([a-zA-Z_]+)"
    _TOKEN_POST = r"(?:[^\(a-zA-Z_]|$)"
    _TOKEN_REGEX = _TOKEN_BODY + _TOKEN_POST
    _DBL_STR_REGEX = r"\"(?:[^\\\"]|\\.)*\""
    _SGL_STR_REGEX = r"\'(?:[^\\\']|\\.)*\'"

    @classmethod
    def ExtractTokensFromExpressions(cls, exprs):
        ret_set = set()
        for expr in exprs:
            if expr == u"*":
                return [u"*"]
            expr_rem = re.sub(cls._DBL_STR_REGEX, r"", expr)
            expr_rem = re.sub(cls._SGL_STR_REGEX, r"", expr_rem)  # string literals removed
            for token in re.findall(cls._TOKEN_REGEX, expr_rem):
                if not token in df.ALL_TOKENS:
                    ret_set.add(token)
        return list(ret_set)

    @classmethod
    def IsAllTokensInAggregate(cls, exprs):
        aggr_regex = r"((?:" + r"|".join(df.AGGREGATE_FUNCTIONS) + r")\((?:(?>[^\(\)]+|(?R))*)\))"
        for expr in exprs:
            expr_rem = re.sub(cls._DBL_STR_REGEX, r"", expr)
            expr_rem = re.sub(cls._SGL_STR_REGEX, r"", expr_rem)  # string literals removed
            while True:
                prev_len = len(expr_rem)
                expr_rem = regex.sub(aggr_regex, r"", expr_rem)  # one aggregate function removed
                if len(expr_rem) == prev_len:
                    break
            if re.search(cls._TOKEN_REGEX, expr_rem):
                return False
        return True

    @classmethod
    def _IsFieldTokenCharacter(cls, ch):
        return ch.isalpha() or ch == u"_"

    @classmethod
    def _IsOperatorCharacter(cls, ch):
        return not ch.isspace()