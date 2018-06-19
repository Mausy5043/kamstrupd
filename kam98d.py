#!/usr/bin/env python3

"""Data post-processor."""

import configparser
import os
import subprocess
import sys
import syslog
import time
import traceback

from random import randrange as rnd

import mausy5043funcs.fileops3 as mf
from mausy5043libs.libdaemon3 import Daemon

# constants
DEBUG       = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID        = "".join(list(filter(str.isdigit,
                                  os.path.realpath(__file__).split('/')[-1])))
MYAPP       = os.path.realpath(__file__).split('/')[-2]
NODE        = os.uname()[1]
GRAPH_UPDATE      = 10   # in minutes
SQL_UPDATE_HOUR   = GRAPH_UPDATE   # in minutes (shouldn't be shorter than GRAPH_UPDATE)
SQL_UPDATE_DAY    = 27  # in minutes
SQL_UPDATE_WEEK   = 4   # in hours
SQL_UPDATE_YEAR   = 8   # in hours


class MyDaemon(Daemon):
  """Override Daemon-class run() function."""
  @staticmethod
  def run():
    iniconf         = configparser.ConfigParser()
    iniconf.read(os.environ['HOME'] + '/' + MYAPP + '/config.ini')
    flock           = iniconf.get(MYID, "lockfile")
    scriptname      = iniconf.get(MYID, "lftpscript")
    sampleTime      = iniconf.getint(MYID, "reporttime") / iniconf.getint(MYID, "samplespercycle")
    sqldata.get(sqldata.h_cmd)
    sqldata.get(sqldata.d_cmd)
    sqldata.get(sqldata.w_cmd)
    sqldata.get(sqldata.y_cmd)
    if trendgraph.draw(trendgraph.command) == 0:
      upload_page(scriptname)
    while True:
      try:
        start_time   = time.time()

        do_stuff(flock, scriptname)

        pause_time    = sampleTime - (time.time() - start_time) - (start_time % sampleTime)
        if pause_time > 0:
          mf.syslog_trace("waiting  ...: {0}s".format(pause_time), False, DEBUG)
          mf.syslog_trace("................................", False, DEBUG)
          time.sleep(pause_time)
      except Exception:
        mf.syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
        mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
        raise


class SqlDataFetch(object):
  """
  SqlDataFetch:
  Manages retrieval of data from the MySQL server
  """
  def __init__(self, h_time, d_time, w_time, y_time):
    super(SqlDataFetch, self).__init__()
    self.home           = os.environ['HOME']
    self.h_dataisstale  = True
    self.h_cmd          = self.home + '/' + MYAPP + '/queries/hour.sh'
    self.h_updatetime   = h_time * 60
    self.h_timer        = time.time() + rnd(60, self.h_updatetime)
    self.d_dataisstale  = True
    self.d_cmd          = self.home + '/' + MYAPP + '/queries/day.sh'
    self.d_updatetime   = d_time * 60
    self.d_timer        = time.time() + rnd(60, self.d_updatetime)
    self.w_dataisstale  = True
    self.w_cmd          = self.home + '/' + MYAPP + '/queries/week.sh'
    self.w_updatetime   = w_time * 3600
    self.w_timer        = time.time() + rnd(60, self.w_updatetime)
    self.y_dataisstale  = True
    self.y_cmd          = self.home + '/' + MYAPP + '/queries/year.sh'
    self.y_updatetime   = y_time * 3600
    self.y_timer        = time.time() + rnd(60, self.y_updatetime)

  def get(self, cmnd):
    """
    Get the requested data.
    """
    mf.syslog_trace("...:  {0}".format(cmnd), False, DEBUG)
    result = subprocess.call(cmnd)
    return not (result == 0)  # return False if successful == data nolonger stale

  def fetch(self):
    """
    Manage staleness of the data and get it when needed.
    """
    ts = time.time()
    t0 = ts
    if t0 >= self.h_timer:
      self.h_dataisstale = self.get(self.h_cmd)
      t1 = time.time()
      self.h_timer = t1 + self.h_updatetime + rnd(-60, 60)
      # dt = t1 - t0  # determine query duration
      t0 = t1
    if t0 >= self.d_timer:
      self.d_dataisstale = self.get(self.d_cmd)
      t1 = time.time()
      self.d_timer = t1 + self.d_updatetime + rnd(-60, 60)
      # dt = t1 - t0  # determine query duration
      t0 = t1
    if t0 >= self.w_timer:
      self.w_dataisstale = self.get(self.w_cmd)
      t1 = time.time()
      self.w_timer = t1 + self.w_updatetime + rnd(-60, 60)
      # dt = t1 - t0  # determine query duration
      t0 = t1
    if t0 >= self.y_timer:
      self.y_dataisstale = self.get(self.y_cmd)
      t1 = time.time()
      self.y_timer = t1 + self.y_updatetime + rnd(-60, 60)
      # dt = t1 - t0  # determine query duration
    return time.time() - ts


class Graph(object):
  """docstring for Graph."""
  def __init__(self, updatetime):
    super(Graph, self).__init__()
    self.home = os.environ['HOME']
    self.updatetime = updatetime * 60
    self.timer      = time.time() + rnd(60, self.updatetime)
    self.command = self.home + '/' + MYAPP + '/mkgraphs.sh'

  def draw(self, cmnd):
    """Draw the graphs"""
    mf.syslog_trace("...:  {0}".format(cmnd), False, DEBUG)
    return subprocess.call(cmnd)

  def make(self):
    t0 = time.time()
    result = 1
    if t0 >= self.timer:
      result = self.draw(self.command)
      t1 = time.time()
      self.timer = t1 + self.updatetime + rnd(-60, 60)
    return result


def do_stuff(flock, script):
  # wait 4 seconds for processes to finish
  # unlock(flock)  # remove stale lock
  time.sleep(4)

  # Retrieve data from MySQL database
  result = sqldata.fetch()
  mf.syslog_trace("...datafetch:  {0}".format(result), False, DEBUG)

  # Create the graphs based on the MySQL data every 3rd minute
  result = trendgraph.make()
  mf.syslog_trace("...trendgrph:  {0}".format(result), False, DEBUG)
  if result == 0:
    upload_page(script)


def upload_page(script):
  try:
    # Upload the webpage and graphs
    if os.path.isfile('/tmp/' + MYAPP + '/site/default.md'):
      write_lftp(script)
      cmnd = ['lftp', '-f', script]
      mf.syslog_trace("...:  {0}".format(cmnd), False, DEBUG)
      cmnd = subprocess.check_output(cmnd, timeout=20)
      mf.syslog_trace("...uploadpag:  {0}".format(cmnd), False, DEBUG)
  except subprocess.TimeoutExpired:
    mf.syslog_trace("***TIMEOUT***:  {0}".format(cmnd), syslog.LOG_ERR, DEBUG)
    time.sleep(17 * 60)             # wait 17 minutes for the router to restart.
    pass
  except subprocess.CalledProcessError:
    mf.syslog_trace("***ERROR***:    {0}".format(cmnd), syslog.LOG_ERR, DEBUG)
    time.sleep(17 * 60)             # wait 17 minutes for the router to restart.
    pass


def write_lftp(script):
  with open(script, 'w') as f:
    f.write('# DO NOT EDIT\n')
    f.write('# This file is created automatically by ' + MYAPP + '\n\n')
    f.write('# lftp script\n\n')
    f.write('set cmd:fail-exit yes;\n')
    f.write('open hendrixnet.nl;\n')
    f.write('cd 05.stream/;\n')
    f.write('set cmd:fail-exit no;\n')
    f.write('mirror --reverse --delete --verbose=3 -c /tmp/' + MYAPP + '/site/ . ;\n')
    f.write('\n')


if __name__ == "__main__":
  daemon = MyDaemon('/tmp/' + MYAPP + '/' + MYID + '.pid')
  trendgraph = Graph(GRAPH_UPDATE)
  sqldata = SqlDataFetch(SQL_UPDATE_HOUR, SQL_UPDATE_DAY, SQL_UPDATE_WEEK, SQL_UPDATE_YEAR)
  syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)  # initialise logging
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
