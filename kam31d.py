#!/usr/bin/env python3

"""Communicates with the smart electricity meter [KAMSTRUP]."""

import configparser
import os
import re
import sys
import syslog
import time
import traceback

import serial

import mausy5043funcs.fileops3 as mf
from mausy5043libs.libdaemon3 import Daemon

# constants
DEBUG       = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID        = "".join(list(filter(str.isdigit,
                                  os.path.realpath(__file__).split('/')[-1])))
MYAPP       = os.path.realpath(__file__).split('/')[-2]
NODE        = os.uname()[1]


class MyDaemon(Daemon):
  """Override Daemon-class run() function."""
  @staticmethod
  def run():
    iniconf = configparser.ConfigParser()
    report_time = iniconf.getint(MYID, "reporttime")
    flock = iniconf.get(MYID, "lockfile")
    fdata = iniconf.get(MYID, "resultfile")
    samples_averaged = (iniconf.getint(MYID, "samplespercycle")
                        * iniconf.getint(MYID, "cycles"))
    sample_time = report_time / iniconf.getint(MYID, "samplespercycle")
    data = []

    port.open()
    serial.XON  # pylint: disable=W0104
    while True:
      try:
        start_time     = time.time()

        result        = do_work()
        result        = result.split(',')
        mf.syslog_trace("Result   : {0}".format(result), False, DEBUG)
        # data.append(list(map(int, result)))
        data.append([int(d) for d in result])
        if len(data) > samples_averaged:
          data.pop(0)
        mf.syslog_trace("Data     : {0}".format(data), False, DEBUG)

        # report sample average
        if start_time % report_time < sample_time:
          # somma       = list(map(sum, zip(*data)))
          somma = [sum(d) for d in zip(*data)]
          # not all entries should be float
          # ['3088596', '3030401', '270', '0', '0', '0', '1', '1']
          # averages    = [format(sm / len(data), '.2f') for sm in somma]
          averages = data[-1]
          averages[2]  = int(somma[2] / len(data))  # avg powerin
          averages[5]  = int(somma[5] / len(data))  # avg powerout
          mf.syslog_trace("Averages : {0}".format(averages), False, DEBUG)
          if averages[0] > 0:
            do_report(averages, flock, fdata)

        pause_time = (sample_time
                      - (time.time() - start_time)
                      - (start_time % sample_time))
        if pause_time > 0:
          mf.syslog_trace("Waiting  : {0}s".format(pause_time), False, DEBUG)
          mf.syslog_trace("................................", False, DEBUG)
          # no need to wait for the next cycles
          # the meter will pace the meaurements
          # any required waiting will be inside gettelegram()
          # time.sleep(pause_time)
        else:
          mf.syslog_trace("Behind   : {0}s".format(pause_time), False, DEBUG)
          mf.syslog_trace("................................", False, DEBUG)
      except Exception:
        mf.syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
        mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
        raise


def do_work():
  """Push the results out to a file."""
  electra1in  = 0
  electra2in  = 0
  powerin     = 0
  electra1out = 0
  electra2out = 0
  powerout    = 0
  tarif       = 0
  swits       = 1

  telegram, status = gettelegram()

  if status == 1:
    for element in range(0, len(telegram)):
      line = re.split(r'[\(\*\)]', telegram[element])
      # ['1-0:1.8.1', '00175.402', 'kWh', '']  T1 in
      if line[0] == '1-0:1.8.1':
        electra1in = int(float(line[1]) * 1000)
      # ['1-0:1.8.2', '00136.043', 'kWh', '']  T2 in
      if line[0] == '1-0:1.8.2':
        electra2in = int(float(line[1]) * 1000)
      # ['1-0:2.8.1', '00000.000', 'kWh', '']  T1 out
      if line[0] == '1-0:2.8.1':
        electra1out = int(float(line[1]) * 1000)
      # ['1-0:2.8.2', '00000.000', 'kWh', '']  T2 out
      if line[0] == '1-0:2.8.2':
        electra2out = int(float(line[1]) * 1000)
      # ['0-0:96.14.0', '0002', '']  tarif 1 or 2
      if line[0] == '0-0:96.14.0':
        tarif = int(line[1])
      # ['1-0:1.7.0', '0000.32', 'kW', '']  power in
      if line[0] == '1-0:1.7.0':
        powerin = int(float(line[1]) * 1000)
      # ['1-0:2.7.0', '0000.00', 'kW', ''] power out
      if line[0] == '1-0:2.7.0':
        powerout = int(float(line[1]) * 1000)
      # ['0-0:17.0.0', '999', 'A', '']
      # not recorded
      # ['0-0:96.3.10', '1', '']  powerusage (1) or powermanufacturing ()
      if line[0] == '0-0:96.3.10':
        swits = int(line[1])
      # ['0-0:96.13.1', '', '']
      # not recorded
      # ['0-0:96.13.0', '', '']
      # not recorded

  return '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(electra1in,
                                                         electra2in,
                                                         powerin,
                                                         electra1out,
                                                         electra2out,
                                                         powerout,
                                                         tarif,
                                                         swits)


def gettelegram():
  """Fetch a telegram from the serialport."""
  # flag used to exit the while-loop
  abort = 0
  # countdown counter used to prevent infinite loops
  loops2go = 40
  # storage space for the telegram
  telegram = []
  # end of line delimiter
  # delim = "\x0a"

  while abort == 0:
    try:
      # line = "".join(iter(lambda: port.read(1), delim)).strip()
      line = str(port.readline().strip(), 'utf-8')
      if line == "!":
        abort = 1
      if line != "":
        telegram.append(line)
    except Exception:
      mf.syslog_trace("*** Serialport read error:", syslog.LOG_CRIT, DEBUG)
      mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
      abort = 2

    loops2go = loops2go - 1
    if loops2go < 0:
      abort = 3

  # test for correct start of telegram
  if telegram[0][0] != "/":
    abort = 2

  # Return codes:
  # abort == 1 indicates a successful read
  # abort == 2 means that a serial port read/write error occurred
  # abort == 3 no valid data after several attempts
  return telegram, abort


def do_report(result, flock, fdata):
  """Push the results out to a file."""
  # Get the time and date in human-readable form and UN*X-epoch...
  OutDate  = time.strftime('%Y-%m-%dT%H:%M:%S')
  OutEpoch = int(time.strftime('%s'))
  result   = ', '.join(map(str, result))
  mf.lock(flock)
  mf.syslog_trace("   @: {0}s".format(OutDate), False, DEBUG)
  with open(fdata, 'a') as fo:
    fo.write('{0}, {1}, {2}\n'.format(OutDate, OutEpoch, result))
  mf.unlock(flock)


if __name__ == "__main__":
  daemon = MyDaemon('/tmp/' + MYAPP + '/' + MYID + '.pid')

  port = serial.Serial()
  port.baudrate = 9600
  port.bytesize = serial.SEVENBITS
  port.parity = serial.PARITY_EVEN
  port.stopbits = serial.STOPBITS_ONE
  port.xonxoff = 1
  port.rtscts = 0
  port.dsrdtr = 0
  port.timeout = 15
  port.port = "/dev/ttyUSB0"

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
