"""Utilities for general operations."""


def PrintResult(table, output):
    if output == "str":
        print(table)
    elif output == "csv":
        print(table.InCsv())
    elif output == "html":
        print(table.InHtml())

def IsNumeric(num_str):