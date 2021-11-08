
"""Parser for SQLGitHub. Outputs SgSession.

Sample Usage:
    g = Github(token)
    parser = SgParser(g)
    s = parser.Parse(["select", "name,", "description", "from", "abseil.repos"])
    print(s.Execute())
    print(parser._ParseOrder(["by", "a+b", "DESC,", "c", "-", "b", "ASC", ",", "a%b"]))
"""

import definition
import session


# TODO(lnishan): Change it to SgParseSimple, modify tokenizer and add SgParser to handle unions and joins.
class SgParser:
    """Parser for SQLGitHub. Outputs SgSession."""
    
    def __init__(self, github):
        self._github = github
        self._Initialize()

    def _Initialize(self):
        self._field_exprs = None
        self._source = None
        self._condition = None
        self._groups = None
        self._having = None
        self._orders = None
        self._limit = None

    def __GetCommaSeparatedExprs(self, tokens_str):
        exprs = []
        in_string = False
        bracket_sum = 0
        is_escaping = False
        expr = u""
        for ch in tokens_str:
            if in_string:
                expr += ch
                if is_escaping:
                    is_escaping = False
                elif ch == "\\":
                    is_escaping = True
                elif ch in (u"\'", u"\""):
                    in_string = False
            elif bracket_sum > 0:
                expr += ch
                if ch == "\"":
                    in_string = True
                elif ch == u"(":
                    bracket_sum = bracket_sum + 1
                elif ch == u")":  # and not in_string
                    bracket_sum = bracket_sum - 1
            else:
                if ch == u",":
                    exprs.append(expr.strip())
                    expr = u""
                else:
                    expr += ch
                    if ch in (u"\'", u"\""):
                        in_string = True
                        is_escaping = False
                    elif ch == u"(":
                        bracket_sum = 1
        if expr:
            exprs.append(expr.strip())
        return exprs

    def _ParseSelect(self, sub_tokens):
        sub_tokens_str = u" ".join(sub_tokens)
        self._field_exprs = self.__GetCommaSeparatedExprs(sub_tokens_str)

    def _ParseFrom(self, sub_tokens):