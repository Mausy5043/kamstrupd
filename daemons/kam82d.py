#!/usr/bin/env python3

"""creates an MD-file."""

import configparser
import os
import platform
import shutil
import sys
import syslog
import time
import traceback

import mausy5043funcs.fileops3 as mf
from mausy5043libs.libdaemon3 import Daemon

# constants
DEBUG       = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID        = "".join(list(filter(str.isdigit, os.path.realpath(__file__).split('/')[-1])))
MYAPP       = os.path.realpath(__file__).split('/')[-2]
NODE        = os.uname()[1]


class MyDaemon(Daemon):
  """Override Daemon-class run() function."""

  # pylint: disable=too-few-public-methods

  @staticmethod
  def run():
    """Execute main loop."""
    iniconf = configparser.ConfigParser()
    iniconf.read(os.environ['HOME'] + '/' + MYAPP + '/config.ini')
    flock       = iniconf.get(MYID,    "lockfile")
    fdata       = iniconf.get(MYID,    "markdown")
    sample_time = iniconf.getint(MYID, "reporttime") / iniconf.getint(MYID, "samplespercycle")

    while True:
      try:
        start_time = time.time()

        do_markdown(flock, fdata)

        pause_time = sample_time - (time.time() - start_time) - (start_time % sample_time)
        if pause_time > 0:
          mf.syslog_trace("Waiting  : {0}s".format(pause_time), False, DEBUG)
          mf.syslog_trace("................................", False, DEBUG)
          time.sleep(pause_time)
      except Exception:
        mf.syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
        mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
        raise


def do_markdown(flock, fdata):
  """Create a MarkDown file."""
  uname = os.uname()

  branch_file = os.environ['HOME'] + "/.kamstrupd.branch"
  with open(branch_file, 'r') as file_handle:
    kamstrupbranch = file_handle.read().strip('\n')

  mf.lock(flock)
  shutil.copyfile(os.environ['HOME'] + '/' + MYAPP + '/default.md', fdata)

  with open(fdata, 'a') as file_handle:
    mf.syslog_trace("writing {0}".format(fdata), False, DEBUG)

    file_handle.write('![A GNUplot image should be here: kamstrup11.png](img/kamstrup11.png)\n')
    file_handle.write('![A GNUplot image should be here: kamstrup12.png](img/kamstrup12.png)\n')
    file_handle.write('![A GNUplot image should be here: kamstrup13.png](img/kamstrup13.png)\n')

    # System ID
    file_handle.write('!!! ')
    file_handle.write(uname[0] + ' ' + uname[1] + ' '
                      + uname[2] + ' ' + uname[3] + ' '
                      + uname[4] + ' ' + platform.platform() + '  \n')

    # branch
    file_handle.write('!!! kamstrupd   on: ' + kamstrupbranch + '  \n')
    file_handle.write('!!! ' + time.strftime("%Y.%m.%d %H:%M") + '\n\n')

  mf.unlock(flock)


if __name__ == "__main__":
  daemon = MyDaemon('/tmp/' + MYAPP + '/' + MYID + '.pid')  # pylint: disable=C0103
  syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)   # initialise logging
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
