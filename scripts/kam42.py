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


def do_add_to_database(result, fdata, sql_cmd):
  """Commit the results to the database."""
  # Get the time and date in human-readable form and UN*X-epoch...
  out_date  = dt.datetime.now()  # time.strftime('%Y-%m-%dT%H:%M:%S')
  out_epoch = int(time.strftime('%s'))
  results = (out_date, out_epoch,
            result[0], result[1], result[2],
            result[3], result[4], result[5],
            result[6], result[7])
  mf.syslog_trace(f"   @: {out_date}", False, DEBUG)
  mf.syslog_trace(f"    : {results}", False, DEBUG)
  conn = create_db_connection(fdata)
  cursor = conn.cursor()
  cursor.execute(sql_cmd, results)
  cursor.close()
  conn.commit()
  conn.close()


def create_db_connection(fdata):
  """ Create a database connection to the SQLite3 database
      specified by database_file
  param database_file: database file
  :return: Connection object or Raise error; will never return None
  """
  mf.syslog_trace(f"Connecting to: {fdata}", False, DEBUG)
  try:
    consql = sqlite3.connect(fdata)
    return consql
  except sqlite3.Error:
    mf.syslog_trace("Unexpected SQLite3 error when connecting to server.", syslog.LOG_CRIT, DEBUG)
    mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
    if consql:    # attempt to close connection to SQLite3 server
      consql.close()
      mf.syslog_trace(" ** Closed SQLite3 connection. **", syslog.LOG_CRIT, DEBUG)
    raise

  return None


def test_db_connection(fdata):
  ''' test & log database engine coonnection
  '''
  try:
    conn = create_db_connection(fdata)
    cursor = conn.cursor()
    cursor.execute("SELECT sqlite_version();")
    versql = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    syslog.syslog(syslog.LOG_INFO, f"Attached to SQLite3 server: {versql}")
  except sqlite3.Error:
    mf.syslog_trace("Unexpected SQLite3 error during test.", syslog.LOG_CRIT, DEBUG)
    mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
    raise


if __name__ == "__main__":
  # initialise logging
  syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)

  iniconf = configparser.ConfigParser()
  fdatabase = os.environ['HOME'] + '/' + iniconf.get(31, "databasefile")
  test_db_connection(fdatabase)
  conn = create_db_connection(fdatabase)

  curs = conn.cursor()
  curs.close()
  conn.close()
