"""Config loader for SQLGitHub."""

import importlib


def Load(module):
    try:
        mod = importlib.import_module(module)
    except ImportError:
        token = None
        output = "str"
    else:
        token = mod