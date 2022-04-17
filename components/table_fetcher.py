
"""Fetches data from GitHub API, store and return the data in a SgTable.

Sample Usage:
    sqlserv = top_level.SQLGitHub(token)
    fetcher = SgTableFetcher(sqlserv._github)
    print(fetcher.Fetch("abseil"))
    print("----------------------------")
    print(fetcher.Fetch("abseil.repos"))
    print("----------------------------")
    print(fetcher.Fetch("abseil.issues"))
    print("----------------------------")
"""

import datetime
import inspect

from github.Commit import Commit
from github.File import File
from github.GitAuthor import GitAuthor
from github.Issue import Issue
from github.Label import Label
from github.NamedUser import NamedUser
from github.Organization import Organization
from github.PullRequest import PullRequest
from github.PullRequestPart import PullRequestPart
from github.Repository import Repository

import table as tb
import utilities as util


class SgTableFetcher:
    """Fetches data from GitHub API, store and return the data in a SgTable."""

    def __init__(self, github, rel_keys=None):
        self._github = github
        self._rel_keys = rel_keys

    def _Parse(self, label):
        tmp = label.split(".")
        if len(tmp) == 1:  # no dots
            return label, None, None
        elif len(tmp) == 2:
            return tmp[0], tmp[1], None
        else:
            return tmp[0], tmp[1], tmp[2:]

    def _GetKeys(self, cls):
        if not u"*" in self._rel_keys:
            # TODO(lnishan): Might want to check for existence of every key in self._rel_keys
            return self._rel_keys
        else:
            return [unicode(key, "utf-8") for key, val in inspect.getmembers(cls, lambda m: not inspect.ismethod(m)) if not key.startswith("_")]

    def __ConvertNonList(self, non_list):
        """Converting these values to make the field "queriable"."""
        if isinstance(non_list, Organization):
            return non_list.name
        elif isinstance(non_list, Repository):
            return non_list.name
        elif isinstance(non_list, Issue):
            return non_list.title
        elif isinstance(non_list, PullRequest):
            return non_list.title
        elif isinstance(non_list, Commit):
            return non_list.commit.message
        elif isinstance(non_list, PullRequestPart):
            return non_list.ref
        elif isinstance(non_list, NamedUser):
            return non_list.login
        elif isinstance(non_list, GitAuthor):
            return non_list.name
        elif isinstance(non_list, Label):
            return non_list.name
        elif isinstance(non_list, File):
            return non_list.filename
        else:
            return non_list

    def __ConvertVal(self, val):
        if isinstance(val, list):
            return [self.__ConvertNonList(non_list) for non_list in val]
        else:
            return self.__ConvertNonList(val)

    def _GetVals(self, cls):
        if not u"*" in self._rel_keys:
            return [self.__ConvertVal(getattr(cls, key)) for key in self._rel_keys]
        else:
            return [self.__ConvertVal(val) for key, val in inspect.getmembers(cls, lambda m: not inspect.ismethod(m)) if not key.startswith("_")]

    def _IsDateRange(self, info):
        if not info:
            return False
        for ch in info:
            if not (util.IsNumeric(ch) or ch == "-"):
                return False
        return True

    def _ParseDateRange(self, info):
        if "-" in info:
            tmp = info.split("-")
            days_start = int(tmp[0]) if tmp[0] else None
            days_end = int(tmp[1]) if tmp[1] else None
            if days_start and days_end and days_start < days_end:
                days_start, days_end = days_end, days_start
            return days_start, days_end
        else:
            return int(info), None

    def _GetDatetimeDaysBefore(self, days):
        return datetime.datetime.now() - datetime.timedelta(days=days)

    def _ExecFuncByDateRange(self, func, days_start, days_end, **kwargs):
        if days_start:
            if days_end:
                return func(since=self._GetDatetimeDaysBefore(days_start),
                            until=self._GetDatetimeDaysBefore(days_end),
                            **kwargs)
            else:
                return func(since=self._GetDatetimeDaysBefore(days_start),
                            **kwargs)