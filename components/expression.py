
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