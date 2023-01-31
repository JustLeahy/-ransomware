#!/usr/bin/env python

import argparse

import config_loader
from components import top_level
from components import utilities as util

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("sql", type=unicode, help="a line of 