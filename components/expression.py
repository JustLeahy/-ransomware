
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

    @classmethod
    def _IsNumericCharacter(cls, ch):
        return ch.isdigit() or ch == u"."

    @classmethod
    def _GetPrecedence(cls, opr):
        return df.PRECEDENCE[opr] if opr else -100

    @classmethod
    def _EvaluateOperatorBack(cls, opds, oprs):
        opr = oprs[-1]
        oprs.pop()
        rows = len(opds)
        if opr == u",":  # special case: have to process every u","
            for i in range(rows):
                opds[i] = opds[i][:-2] + [opds[i][-2] + [opds[i][-1]]]
        elif opr == u"*":
            for i in range(rows):
                res = opds[i][-2] * opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"/":
            for i in range(rows):
                res = opds[i][-2] / opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"%":
            for i in range(rows):
                res = opds[i][-2] % opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"+":
            for i in range(rows):
                res = opds[i][-2] + opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"-":
            for i in range(rows):
                res = opds[i][-2] - opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"==":  # shouldn't work with None but it does atm
            for i in range(rows):
                res = opds[i][-2] == opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u">=":
            for i in range(rows):
                res = opds[i][-2] >= opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u">":
            for i in range(rows):
                res = opds[i][-2] > opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"<=":
            for i in range(rows):
                res = opds[i][-2] <= opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"<":
            for i in range(rows):
                res = opds[i][-2] < opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"<>":
            for i in range(rows):
                res = opds[i][-2] != opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"!=":
            for i in range(rows):
                res = opds[i][-2] != opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"is":
            for i in range(rows):
                res = opds[i][-2] == opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"like":
            for i in range(rows):
                is_escaping = False
                regex = r""
                for ch in opds[i][-1]:
                    if is_escaping:  # \% \_
                        regex += ch
                        is_escaping = False
                    elif ch == "\\":
                        is_escaping = True
                    elif ch == "%":
                        regex += ".*"
                    elif ch == "_":
                        regex += "."
                    else:
                        regex += re.escape(ch)
                regex += r"$"
                res = True if opds[i][-2] and re.match(regex, opds[i][-2]) else False
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"regexp":
            for i in range(rows):
                regex = re.compile(opds[i][-1] + "$")
                res = True if opds[i][-2] and re.match(regex, opds[i][-2]) else False
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"in":
            for i in range(rows):
                res = opds[i][-2] in opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"not":
            for i in range(rows):
                opds[i][-1] = not opds[i][-1]
        elif opr in (u"and", u"&&"):
            for i in range(rows):
                res = opds[i][-2] and opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == "xor":
            for i in range(rows):
                res = opds[i][-2] != opds[i][-1]  # assumes both are boolean's
                opds[i] = opds[i][:-2] + [res]
        elif opr in (u"or", u"||"):
            for i in range(rows):
                res = opds[i][-2] or opds[i][-1]
                opds[i] = opds[i][:-2] + [res]

    @classmethod
    def _EvaluateFunction(cls, opds, func):
        # TODO(lnishan): Add new function names to definitions.py
        rows = len(opds)
        if func == "zero":  # dummy function
            return [0] * rows
        if func == "avg":
            avg = sum(row[-1] for row in opds) / float(rows)
            res = []
            for i in range(rows):
                res.append(avg)
            return res
        elif func == "count":
            res = []
            for i in range(rows):
                res.append(rows)
            return res
        elif func == "max":
            mx = max(row[-1] for row in opds)
            res = []
            for i in range(rows):
                res.append(mx)
            return res
        elif func == "min":
            mn = min(row[-1] for row in opds)
            res = []
            for i in range(rows):
                res.append(mn)
            return res
        elif func == "sum":
            sm = sum(row[-1] for row in opds)
            res = []
            for i in range(rows):
                res.append(sm)
            return res
        elif func == "ascii":
            res = []
            for row in opds:
                res.append(u" ".join(str(ord(i)) for i in row[-1]))
            return res
        elif func == "concat":
            res = []
            for row in opds:
                cstr = u""
                for val in row[-1]:
                    cstr += util.GuaranteeUnicode(val)
                res.append(cstr)
            return res
        elif func == "concat_ws":
            res = []
            for row in opds:
                cstr = u""
                sep = row[-1][0]
                for val in row[-1][:-1]:
                    if val != sep:
                        cstr += util.GuaranteeUnicode(val)
                        cstr += sep
                cstr += util.GuaranteeUnicode(row[-1][-1])
                res.append(cstr)
            return res
        elif func == "find_in_set":
            res =[]
            for row in opds:
                cstr = row[-1][-1]
                subs = row[-1][-2]
                if subs in cstr:
                    res.append(cstr.index(subs)+1)
                else:
                    res.append(0)
            return res
        elif func == "insert":
            res = []
            for row in opds:
                x = row[-1][-3] - 1
                y = row[-1][-2]
                str = row[-1][-4]
                subs = row[-1][-1]
                res.append(str[:x] + subs + str[x+y-1:])
            return res
        elif func == "instr":
            res = []
            for row in opds:
                res.append(row[-1][-2].find(row[-1][-1])+1)
            return res
        elif func in (u"lcase", u"lower"):
            res = []
            for row in opds:
	        res.append(row[-1].lower())
            return res
        elif func == "left":
            res = []
            for row in opds:
                n_char = row[-1][-1]
                subs = row[-1][-2]
                res.append(subs[:n_char])
            return res
        elif func == "length":
            res = []
            for row in opds:
                res.append(len(row[-1]))
            return res
        elif func == "locate":
            res = []
            for row in opds:
                x = len(row[-1])
                if x == 3:
                    st_pos = row[-1].pop()
                cstr = row[-1].pop()
                subs = row[-1].pop()
                if x == 3:
                    res.append(cstr.find(subs, st_pos)+1)
                else:
                    res.append(cstr.find(subs)+1)
            return res
        elif func in (u"mid", u"substr", u"substring"):
            res = []
            for row in opds:
                x = len(row[-1])
                if x == 3:
                    n_len = row[-1].pop()
                n_st = row[-1].pop() - 1
                subs = row[-1].pop()
                if x == 3:
                    n_end = n_st + n_len
                    res.append(subs[n_st:n_end]) 
                else:
                    res.append(subs[n_st:])
            return res 
        elif func == "repeat":
            res = []
            for row in opds:
                cstr = u""
                for i in range(row[-1][-1]):
                    cstr += row[-1][-2]
                res.append(cstr)
            return res
        elif func == "replace":
            res = []
            for row in opds:
                res.append(row[-1][-3].replace(row[-1][-2],row[-1][-1]))
            return res  
        elif func == "right":
            res = []
            for row in opds:
                n_char = row[-1][-1]
                subs = row[-1][-2]
                res.append(subs[-n_char:])
            return res
        elif func == "strcmp":
            res = []
            for row in opds:
                res.append((row[-1][-1] == row[-1][-2]))
            return res
        elif func in (u"ucase", u"upper"):
            res = []