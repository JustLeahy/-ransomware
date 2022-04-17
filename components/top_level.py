
import sys
import time

from github import Github
from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import style_from_pygments
from pygments.lexers.sql import MySqlLexer
from pygments.styles.monokai import MonokaiStyle

import definition
import parser
import utilities as util
import tokenizer


class SQLGitHub:
    """Meta Component for SQLGitHub."""

    _PROMPT_STR = u"SQLGitHub> "

    def __init__(self, token, output="str"):
        self._github = Github(token)
        self._output = output
        self._parser = parser.SgParser(self._github)
        self._completer = WordCompleter(definition.ALL_TOKENS,
                                        ignore_case=True)
        self._style = style_from_pygments(MonokaiStyle)

    def Execute(self, sql, display_result=True):
        if not sql:
            return
        start_time = time.time()
        tokens = tokenizer.SgTokenizer.Tokenize(sql)
        try:
            session = self._parser.Parse(tokens)
        except NotImplementedError:
            sys.stderr.write("Not implemented command tokens in SQL.\n")
        except SyntaxError:
            sys.stderr.write("SQL syntax incorrect.\n")
        else:
            try:
                result = session.Execute()
            except AttributeError: