#!/usr/bin/env python3

"""Communicates with the smart electricity meter [KAMSTRUP]."""

import configparser
import datetime as dt
import os
import re
import sqlite3
import sys
import syslog
import time
import traceback

import mausy5043funcs.fileops3 as mf

# constants
DEBUG       = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID        = "".join(list(filter(str.isdigit, os.path.realpath(__file__).split('/')[-1])))
MYAPP       = os.path.realpath(__file__).split('/')[-3]
NODE        = os.uname()[1]


def get_cli_params():
    """Check for presence of a CLI parameter."""
    if len(sys.argv) != 2:
        sys.exit(0)
    # 1 parameter required = filename to be processed
    return sys.argv[1]


def read_file(file_to_read_from):
    """
    Return the contents of a file if it exists.

    Abort if it doesn't exist.
    """
    if not os.path.isfile(file_to_read_from):
        sys.exit(0)
    with open(file_to_read_from, 'r') as input_file:
        # read the inputfile
        return input_file.read().splitlines()


def write_file(file_to_write_to, lines_to_write):
    """
    Output <lines_to_write> to the file <file_to_write_to>.

    Will overwrite existing file.
    """
    with open(file_to_write_to, 'w') as output_file:
        for line in lines_to_write:
            output_file.write(f'{line}\n')


if __name__ == "__main__":
  # initialise logging
  syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)
  ifile = get_cli_params()
  lines = read_file(ifile)
  print(lines.split(', '))
