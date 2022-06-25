"""Utilities for general operations."""


def PrintResult(table, output):
    if output == "str":
        print(table)
    elif output == "csv":
        print(table.InCsv())
    elif output == "html":
        print(table.InHtml())

def IsNumeric(num_str):
    try:
        val = int(num_str)
    except ValueError:
        return False
    else:
        return True

def GuaranteeUnicode(obj):
    if type(obj) == unicode:
        return obj
    elif type(obj) == str:
        return uni