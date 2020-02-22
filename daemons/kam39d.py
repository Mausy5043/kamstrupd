#!/usr/bin/env python3

"""
Communicate with the SolarEdge API to fetch energy production data.

- produced energy

Store the data in a sqlite3 database.
"""

import configparser
import datetime as dt
import os
import sqlite3
import sys
import syslog
import time
import traceback

# noinspection PyUnresolvedReferences
import mausy5043funcs.fileops3 as mf
import solaredge
# noinspection PyUnresolvedReferences
from mausy5043libs.libdaemon3 import Daemon

# constants
DEBUG = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID = "".join(list(filter(str.isdigit, os.path.realpath(__file__).split('/')[-1])))
MYAPP = os.path.realpath(__file__).split('/')[-3]
NODE = os.uname()[1]


# noinspection PyUnresolvedReferences
class MyDaemon(Daemon):
  """Override Daemon-class run() function."""

  # pylint: disable=too-few-public-methods

  # noinspection PyUnresolvedReferences
  @staticmethod
  def run():
    """Execute main loop."""
    # read api_key from the file ~/.config/solaredge/account.ini
    iniconf = configparser.ConfigParser()
    iniconf.read(f"{os.environ['HOME']}/.config/solaredge/account.ini")
    api_key = iniconf.get('account', 'api_key')
    # read the rest of the configuration from config.ini
    iniconf = configparser.ConfigParser()
    iniconf.read(f"{os.environ['HOME']}/{MYAPP}/config.ini")
    report_time = iniconf.getint(MYID, "reporttime")
    fdatabase = f"{os.environ['HOME']}/{iniconf.get(MYID, 'databasefile')}"
    sqlcmd = iniconf.get(MYID, 'sqlcmd')
    samples_averaged = iniconf.getint(MYID, 'samplespercycle') * iniconf.getint(MYID, 'cycles')
    sample_time = report_time / iniconf.getint(MYID, 'samplespercycle')
    data = []

    test_db_connection(fdatabase)

    api = solaredge.Solaredge(api_key)

    try:
      site_list = api.get_list()['sites']['site']
    except Exception:
      mf.syslog_trace("Error connecting to SolarEdge", syslog.LOG_CRIT, DEBUG)
      mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
      raise

    while True:
      try:
        start_time = time.time()
        data = do_work(api, site_list)
        if data:
          mf.syslog_trace(f"Data to add : {data}", False, DEBUG)
          do_add_to_database(data, fdatabase, sqlcmd)

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


def do_work(api, site_list):
  """Extract the data from the dict(s)."""
  dt_format = '%Y-%m-%d %H:%M:%S'
  data_list = list()

  for site in site_list:
    site_id = site['id']
    data_dict = api.get_overview(site_id)['overview']
    """
    data_dict looks like this:
    { 'currentPower': {'power': 353.82956},
      'lastDayData': {'energy': 219.0},
      'lastMonthData': {'energy': 105406.0},
      'lastUpdateTime': '2020-02-20 09:58:33',
      'lastYearData': {'energy': 203548.0},
      'lifeTimeData': {'energy': 405694.0},
      'measuredBy': 'INVERTER'
    }
    """
    try:
      date_time = data_dict['lastUpdateTime']
      epoch = int(dt.datetime.strptime(date_time, dt_format).timestamp())
      energy = data_dict['lifeTimeData']['energy']
      data_list.append([date_time, epoch, site_id, energy])
      mf.syslog_trace(f"    : {date_time} = {energy}", False, DEBUG)
    except TypeError:
      # ignore empty sites
      continue
    except:
      mf.syslog_trace(f"****: {site_id} ", False, DEBUG)
      mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
      continue

  return data_list


def do_add_to_database(result_data, fdatabase, sql_cmd):
  """Commit the results to the database."""
  conn = None
  cursor = None
  # we don't record the datetime of addition to the database here.
  # instead we use the datetime we got from the SolarEdge database.
  # So, we can just dump the data into sqlite3.
  for entry in result_data:
    results = tuple(entry)

    err_flag = True
    while err_flag:
      try:
        conn = create_db_connection(fdatabase)
        cursor = conn.cursor()
        if not epoch_is_present_in_database(cursor, results[1], results[2]):
          mf.syslog_trace(f"   @: {results[0]} = {results[2]}", False, DEBUG)
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


def epoch_is_present_in_database(db_cur, epoch, site_id):
  """
  Test if results is already present in the database
  :param db_cur: object database-cursor
  :param epoch: int
  :param site_id: int
  :return: boolean  (true if data is present in the database for the given site at or after the given epoch)
  """
  db_cur.execute(f"SELECT MAX(sample_epoch) \
                   FROM production \
                   WHERE (site_id = 0) OR (site_id = {site_id}) \
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
