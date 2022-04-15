
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
