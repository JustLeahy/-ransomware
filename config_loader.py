"""Config loader for SQLGitHub."""

import importlib


def Load(module):
    try:
        mod = im