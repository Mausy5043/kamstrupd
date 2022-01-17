#!/usr/bin/env python3

"""
Communicate with the smart electricity meter [KAMSTRUP].

Store data from a Kamstrup smart-electricity meter in a sqlite3 database.
"""

import argparse
import contextlib
import os
import re
import sqlite3
import syslog
import time
import traceback

import mausy5043funcs.fileops3 as mf
import mausy5043libs.libsqlite3 as msql
import mausy5043libs.libsignals3 as ml
import libkamstrup as lk
import serial

import constants

from hanging_threads import start_monitoring
anti_freeze = constants.KAMSTRUP['report_time'] * 2

parser = argparse.ArgumentParser(description="Execute the telemetry daemon.")
parser_group = parser.add_mutually_exclusive_group(required=True)
parser_group.add_argument("--start",
                          action="store_true",
                          help="start the daemon as a service"
                          )
parser_group.add_argument("--debug",
                          action="store_true",
                          help="start the daemon in debugging mode"
                          )
OPTION = parser.parse_args()

# constants
DEBUG = False
HERE = os.path.realpath(__file__).split("/")
# runlist id :
MYID = HERE[-1]
# app_name :
MYAPP = HERE[-3]
MYROOT = "/".join(HERE[0:-3])
# host_name :
NODE = os.uname()[1]


# example values:
# HERE: ['', 'home', 'pi', 'kamstrupd', 'bin', 'kamstrup.py']
# MYID: 'kamstrup.py
# MYAPP: kamstrupd
# MYROOT: /home/pi
# NODE: rbelec


def main():
    """Execute main loop."""
    global DEBUG
    killer = ml.GracefulKiller()
    start_monitoring(seconds_frozen=anti_freeze, test_interval=2000)
    fdatabase = constants.KAMSTRUP['database']
    sqlcmd = constants.KAMSTRUP['sql_command']
    sqltable = constants.KAMSTRUP['sql_table']
    report_time = int(constants.KAMSTRUP['report_time'])
    samples_averaged = int(constants.KAMSTRUP['samplespercycle']) \
                       * int(constants.KAMSTRUP['cycles'])
    sample_time = report_time / int(constants.KAMSTRUP['samplespercycle'])
    data_frame = None

    msql.test_db_connection(fdatabase)
    # noqa
    pause_time = time.time()
    while not killer.kill_now:
        if time.time() > pause_time:
            start_time = time.time()
            succes = kamstrup.get_telegram()
            if succes:
                if DEBUG:
                    print(f"Result   : {kamstrup.dict_data}")
                # TODO: INSERT data <kamstrup.list_data> into DB <fdatabase> using command <sqlcmd>
                # returns empty list if succesful or items not inserted
                kamstrup.listdata = msql.insert_data(kamstrup.listdata, fdatabase, sqlcmd)

            # report sample average
            if start_time % report_time < sample_time:
                # somma       = list(map(sum, zip(*data)))
                somma = [sum(d) for d in zip(*data)]
                # not all entries should be float
                # ['3088596', '3030401', '270', '0', '0', '0', '1', '1']
                # averages    = [format(sm / len(data), '.2f') for sm in somma]
                averages = data[-1]
                averages[2] = int(somma[2] / len(data))  # avg powerin
                averages[5] = int(somma[5] / len(data))  # avg powerout
                mf.syslog_trace(f"Averages : {averages}", False, DEBUG)
                if averages[0] > 0:
                    msql.insert(averages, fdatabase, sqltable)

            pause_time = (sample_time
                          - (time.time() - start_time)
                          - (start_time % sample_time)
                          + time.time()
                          )
            if pause_time > 0:
                mf.syslog_trace(f"Waiting  : {pause_time - time.time():.1f}s", False, DEBUG)
                # no need to wait for the next cycles
                # the meter will pace the meaurements
                # any required waiting will be inside gettelegram()
                # time.sleep(pause_time)
                mf.syslog_trace("................................", False, DEBUG)
            else:
                mf.syslog_trace(
                    f"Behind   : {pause_time - time.time():.1f}s",
                    False,
                    DEBUG,
                )
                mf.syslog_trace("................................", False, DEBUG)
        else:
            time.sleep(1.0)


if __name__ == "__main__":
    if OPTION.debug:
        DEBUG = True
        mf.syslog_trace("Debug-mode started.", syslog.LOG_DEBUG, DEBUG)
        print("Use <Ctrl>+C to stop.")

    kamstrup = lk.Kamstrup(debug=DEBUG)
    # OPTION.start only executes this next line, we don't need to test for it.
    main()

    print("And it's goodnight from him")
