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


if __name__ == "__main__":
  # initialise logging
  syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)
