
"""Language definitions for SQLGitHub."""


COMMAND_TOKENS = [u"select", u"from", u"where", u"group", u"having", u"order", u"limit"]
EXIT_TOKENS = [u"exit", u"q"]
OPERATOR_TOKENS = [u"interval",
                   u"binary", u"collate",
                   u"!",
                   u"-", u"~",
                   u"^",
                   u"*", u"/", u"div", u"%", u"mod",
                   u"-", u"+",
                   u"<<", u">>",
                   u"&",
                   u"|",
                   u"=", u"<=>", u">=", u">", u"<=", u"<", u"<>", u"!=", u"is", u"like", u"regexp", u"in",
                   u"between", u"case", u"when", u"then", u"else",
                   u"not",
                   u"and", u"&&",
                   u"xor",
                   u"or", u"||",
                   u"=", u":=",
                   u",",
                   u"(",
                   u")"]

AGGREGATE_FUNCTIONS = ["avg", "count", "max", "min", "sum"]