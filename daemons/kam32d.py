#!/usr/bin/env python3

"""
Communicate with the weatherstation website [GILZE-RIJEN] to fetch relevant weather data.

- temperature
- solar radiation

Store the data from the website of buienradar.nl in a sqlite3 database.
"""

import configparser
import datetime as dt
import json
import os
import sqlite3
import sys
import syslog
import time
import traceback
import urllib.request

# noinspection PyUnresolvedReferences
import mausy5043funcs.fileops3 as mf
# noinspection PyUnresolvedReferences
from mausy5043libs.libdaemon3 import Daemon

# constants
DEBUG = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID = "".join(list(filter(str.isdigit, os.path.realpath(__file__).split('/')[-1])))
MYAPP = os.path.realpath(__file__).split('/')[-3]
NODE = os.uname()[1]
T_MEMORY = None
S_MEMORY = None

URL = "https://api.buienradar.nl/data/public/1.1/jsonfeed"


# noinspection PyUnresolvedReferences
class MyDaemon(Daemon):
  """Override Daemon-class run() function."""

  # pylint: disable=too-few-public-methods

  # noinspection PyUnresolvedReferences
  @staticmethod
  def run():
    """Execute main loop."""
    iniconf = configparser.ConfigParser()
    iniconf.read(f"{os.environ['HOME']}/{MYAPP}/config.ini")
    report_time = iniconf.getint(MYID, "reporttime")
    fdatabase = f"{os.environ['HOME']}/{iniconf.get(MYID, 'databasefile')}"
    sqlcmd = iniconf.get(MYID, 'sqlcmd')
    samples_averaged = iniconf.getint(MYID, 'samplespercycle') * iniconf.getint(MYID, 'cycles')
    sample_time = report_time / iniconf.getint(MYID, 'samplespercycle')
    data = []

    test_db_connection(fdatabase)

    while True:
      try:
        start_time = time.time()
        data = do_work()
        if data:
          mf.syslog_trace(f"Data to add : {data}", False, DEBUG)
          do_add_to_database(data, fdatabase, sqlcmd)
        """
        result = result.split(',')
        mf.syslog_trace(f"Result   : {result}", False, DEBUG)
        # data.append(list(map(int, result)))
        data.append([float(d) for d in result])
        if len(data) > samples_averaged:
          data.pop(0)
        mf.syslog_trace(f"Data     : {data}", False, DEBUG)

        # report sample average
        if start_time % report_time < sample_time:
          # somma       = list(map(sum, zip(*data)))
          somma = [sum(d) for d in zip(*data)]
          # not all entries should be float
          # ['3088596', '3030401', '270', '0', '0', '0', '1', '1']
          averages = [format(sm / len(data), '.2f') for sm in somma]
          averages[1] = float(somma[0] / len(data))  # avg temperature
          averages[2] = float(somma[1])  # total solar radiation
          mf.syslog_trace(f"Averages : {averages}", False, DEBUG)
          if averages[0] > 0:
            do_add_to_database(averages, fdatabase, sqlcmd)
        """

        pause_time = (sample_time
                      - (time.time() - start_time)
                      - (start_time % sample_time))
        if pause_time > 0:
          mf.syslog_trace(f"Waiting  : {pause_time}s", False, DEBUG)
          mf.syslog_trace("................................", False, DEBUG)
          time.sleep(pause_time)
        else:
          mf.syslog_trace(f"Behind   : {pause_time}s", False, DEBUG)
          mf.syslog_trace("................................", False, DEBUG)
      except Exception:
        mf.syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
        mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
        raise


def do_work():
  """Push the results out to a file."""
  global T_MEMORY
  global S_MEMORY
  dt_format = '%m/%d/%Y %H:%M:%S'
  temperature = T_MEMORY
  solrad = S_MEMORY
  date_time = ''
  epoch = 0

  station_data = gettelegram()

  for stn in station_data:
    if int(stn['@id']) == 6350:
      for key in stn:
        if key == 'temperatuurGC':
          temperature = stn[key].strip()
        if key == 'zonintensiteitWM2':
          solrad = stn[key].strip()
          if solrad == '-':
            solrad = '0'
        if key == 'datum':
          date_time = stn[key].strip()
          epoch = int(dt.datetime.strptime(date_time, dt_format).timestamp())

  T_MEMORY = temperature
  S_MEMORY = solrad

  return [date_time, epoch, temperature, solrad]


# noinspection PyUnresolvedReferences
def gettelegram():
  """Fetch current weather from website."""
  retries = 4
  while True:
    try:
      response = urllib.request.urlopen(URL)
      data = json.loads(response.read())
      # only return current station info
      stns = data['buienradarnl']['weergegevens']['actueel_weer']['weerstations']['weerstation']
    except:
      retries -= 1
      if retries:
        time.sleep(30)
        continue
      else:
        stns = {}
        break
    break

  return stns


def do_add_to_database(results, fdatabase, sql_cmd):
  """Commit the results to the database."""
  # Get the time and date in human-readable form and UN*X-epoch...
  conn = None
  cursor = None
  # we don't record the datetime of addition to the database here.
  # instead we use the datetime we got from buienradar.
  # So, we can just dump the data into sqlite3.
  mf.syslog_trace(f"   @: {result[0]}", False, DEBUG)
  mf.syslog_trace(f"    : {results[1:]}", False, DEBUG)

  err_flag = True
  while err_flag:
    try:
      conn = create_db_connection(fdatabase)
      cursor = conn.cursor()
      # cursor.execute(sql_cmd, results)
      # cursor.close()
      # conn.commit()
      # conn.close()
      if not epoch_is_present_in_database(cursor, results[1]):
        mf.syslog_trace(f"   @: {results[0]} = {results[2]} {results[3]}", False, DEBUG)
        cursor.execute(sql_cmd, results)
        cursor.close()
        conn.commit()
        conn.close()
      else:
        mf.syslog_trace(f"Skip: {results[0]}", False, DEBUG)
      err_flag = False
    except sqlite3.OperationalError:
      if cursor:
        cursor.close()
      if conn:
        conn.close()


def epoch_is_present_in_database(db_cur, epoch):
  """
  Test if results is already present in the database
  :param db_cur: object database-cursor
  :param epoch: int
  :param site_id: int
  :return: boolean  (true if data is present in the database for the given site at or after the given epoch)
  """
  db_cur.execute(f"SELECT MAX(sample_epoch) \
                   FROM weather \
                   ;"
                 )
  db_epoch = db_cur.fetchone()[0]
  if db_epoch >= epoch:
    return True
  return False


def create_db_connection(database_file):
  """
  Create a database connection to the SQLite3 database specified by database_file.
  """
  consql = None
  mf.syslog_trace(f"Connecting to: {database_file}", False, DEBUG)
  try:
    consql = sqlite3.connect(database_file, timeout=9000)
    # if consql:    # dB initialised succesfully -> get a cursor on the dB and run a test.
    #  cursql = consql.cursor()
    #  cursql.execute("SELECT sqlite_version()")
    #  versql = cursql.fetchone()
    #  cursql.close()
    #  logtext = f"Attached to SQLite3 server : {versql}"
    #  syslog.syslog(syslog.LOG_INFO, logtext)
    return consql
  except sqlite3.Error:
    mf.syslog_trace("Unexpected SQLite3 error when connecting to server.", syslog.LOG_CRIT, DEBUG)
    mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
    if consql:  # attempt to close connection to SQLite3 server
      consql.close()
      mf.syslog_trace(" ** Closed SQLite3 connection. **", syslog.LOG_CRIT, DEBUG)
    raise


def test_db_connection(fdatabase):
  """
  Test & log database engine connection.
  """
  try:
    conn = create_db_connection(fdatabase)
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
  daemon = MyDaemon(f'/tmp/{MYAPP}/{MYID}.pid')  # pylint: disable=C0103

  # initialise logging
  syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)

  if len(sys.argv) == 2:
    if sys.argv[1] == 'start':
      daemon.start()
    elif sys.argv[1] == 'stop':
      daemon.stop()
    elif sys.argv[1] == 'restart':
      daemon.restart()
    elif sys.argv[1] == 'debug':
      # assist with debugging.
      print("Debug-mode started. Use <Ctrl>+C to stop.")
      DEBUG = True
      mf.syslog_trace("Daemon logging is ON", syslog.LOG_DEBUG, DEBUG)
      daemon.run()
    else:
      print("Unknown command")
      sys.exit(2)
    sys.exit(0)
  else:
    print("usage: {0!s} start|stop|restart|debug".format(sys.argv[0]))
    sys.exit(2)
