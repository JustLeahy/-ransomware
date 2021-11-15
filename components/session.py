
"""A class for SQLGitHub sessions.

Sample Usage:
    g = Github(token)
    s = SgSession(g, ["name", "description"], "abseil.repos")
    print(s.Execute())
"""

import table as tb
import table_fetcher
from expression import SgExpression
from grouping import SgGrouping
from ordering import SgOrdering
from ordering import SgTableOrdering


# TODO(lnishan): Change it to SgSessionSimple and add SgSession to handle unions and joins.
class SgSession:
    """A class for SQLGitHub sessions."""

    def __init__(self, github, field_exprs, source=None, condition=None, groups=None, having=None, orders=None, limit=None):
        self._field_exprs = field_exprs
        self._source = source
        self._condition = condition
        self._groups = groups
        self._having = having
        self._orders = orders
        self._limit = limit

        rel_keys = SgExpression.ExtractTokensFromExpressions(self._field_exprs)
        if self._condition:
            rel_keys += SgExpression.ExtractTokensFromExpressions([self._condition])
        if self._groups:
            rel_keys += SgExpression.ExtractTokensFromExpressions(self._groups)
        if self._having:
            rel_keys += SgExpression.ExtractTokensFromExpressions([self._having])
        if self._orders:
            rel_keys += SgExpression.ExtractTokensFromExpressions(self._orders[0])
        rel_keys = list(set(rel_keys))
        if u"*" in rel_keys:
            rel_keys = [u"*"]
        self._fetcher = table_fetcher.SgTableFetcher(github, rel_keys)

    def _GetEmptyTable(self):
        table = tb.SgTable()
        table.SetFields(self._field_exprs)
        return table

    def Execute(self):
        # source is either a label (eg. "google.issues") or a SgSession
        if self._source:
            source_table = self._source.Execute() if isinstance(self._source, SgSession) else self._fetcher.Fetch(self._source)
            if not source_table[:]:
                return self._GetEmptyTable()
            else:
                if u"*" in self._field_exprs:
                    self._field_exprs = source_table.GetFields()
        else:
            source_table = tb.SgTable()
            source_table.SetFields([u"Dummy Field"])
            source_table.Append([u"Dummy Value"])

        # evaluate where
        if self._condition:
            filtered_table = tb.SgTable()
            filtered_table.SetFields(source_table.GetFields())
            meets = SgExpression.EvaluateExpression(source_table, self._condition)
            for i, row in enumerate(source_table):
                if meets[i]:
                    filtered_table.Append(row)
        else:
            filtered_table = source_table
        if not filtered_table[:]: