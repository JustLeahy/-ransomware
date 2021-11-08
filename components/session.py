
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