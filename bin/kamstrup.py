#!/usr/bin/env python3

"""
Communicate with the smart electricity meter [KAMSTRUP].

Store data from a Kamstrup smart-electricity meter in a sqlite3 database.
"""

import argparse
import configparser
import datetime as dt
import os
import re
import sqlite3
import syslog
import time
import traceback

import mausy5043funcs.fileops3 as mf
import mausy5043libs.libsignals3 as ml
import serial

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

electra1in = 0
electra2in = 0
powerin = 0
electra1out = 0
electra2out = 0
powerout = 0
tarif = 0
swits = 0


def main():
    """Execute main loop."""
    global PORT
    killer = ml.GracefulKiller()
    iniconf = configparser.ConfigParser()
    iniconf.read(f"{os.environ['HOME']}/{MYAPP}/config.ini")
    report_time = iniconf.getint(MYID, "reporttime")
    fdatabase = f"{os.environ['HOME']}/{iniconf.get(MYID, 'databasefile')}"
    sqlcmd = iniconf.get(MYID, "sqlcmd")
    samples_averaged = iniconf.getint(MYID,
                                      "samplespercycle"
                                      ) * iniconf.getint(MYID, "cycles")
    sample_time = report_time / iniconf.getint(MYID, "samplespercycle")
    data = []

    test_db_connection(fdatabase)

    PORT.open()
    serial.XON  # noqa
    pause_time = time.time()
    while not killer.kill_now:
        if time.time() > pause_time:
            start_time = time.time()
            result = do_work()
            result = result.split(",")
            mf.syslog_trace(f"Result   : {result}", False, DEBUG)
            # data.append(list(map(int, result)))
            data.append([int(d) for d in result])
            if len(data) > samples_averaged:
                data.pop(0)
            # mf.syslog_trace(f"Data     : {data}", False, DEBUG)

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
                    do_add_to_database(averages, fdatabase, sqlcmd)

            pause_time = (sample_time
                          - (time.time() - start_time)
                          - (start_time % sample_time)
                          + time.time()
                          )
            if pause_time > 0:
                mf.syslog_trace(f"Waiting  : {pause_time - time.time():.1f}s",
                                False,
                                DEBUG,
                                )
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


def do_work():
    """Push the results out to a file."""
    global electra1in
    global electra2in
    global powerin
    global electra1out
    global electra2out
    global powerout
    global tarif
    global swits
    # swits is not always present. The value will
    # change *if* present in the telegram.
    swits = 0
    telegram, status = gettelegram()

    if status == 1:
        for element in telegram:
            try:
                line = re.split(r"[\(\*\)]", element)  # noqa
                # ['1-0:1.8.1', '00175.402', 'kWh', '']  T1 in
                if line[0] == "1-0:1.8.1":
                    electra1in = int(float(line[1]) * 1000)
                # ['1-0:1.8.2', '00136.043', 'kWh', '']  T2 in
                if line[0] == "1-0:1.8.2":
                    electra2in = int(float(line[1]) * 1000)
                # ['1-0:2.8.1', '00000.000', 'kWh', '']  T1 out
                if line[0] == "1-0:2.8.1":
                    electra1out = int(float(line[1]) * 1000)
                # ['1-0:2.8.2', '00000.000', 'kWh', '']  T2 out
                if line[0] == "1-0:2.8.2":
                    electra2out = int(float(line[1]) * 1000)
                # ['0-0:96.14.0', '0002', '']  tarif 1 or 2
                if line[0] == "0-0:96.14.0":
                    tarif = int(line[1])
                # ['1-0:1.7.0', '0000.32', 'kW', '']  power in
                if line[0] == "1-0:1.7.0":
                    powerin = int(float(line[1]) * 1000)
                # ['1-0:2.7.0', '0000.00', 'kW', ''] power out
                if line[0] == "1-0:2.7.0":
                    powerout = int(float(line[1]) * 1000)
                # ['0-0:17.0.0', '999', 'A', ''] unknown; not recorded
                # ['0-0:96.3.10', '1', '']  powerusage (1)
                #                           or powermanufacturing ()
                if line[0] == "0-0:96.3.10":
                    swits = int(line[1])
                # ['0-0:96.13.1', '', '']
                # not recorded
                # ['0-0:96.13.0', '', '']
                # not recorded
            except ValueError:
                mf.syslog_trace("*** Conversion not possible for element:",
                                syslog.LOG_CRIT,
                                DEBUG,
                                )
                mf.syslog_trace(f"    {element}", syslog.LOG_CRIT, DEBUG)
                mf.syslog_trace("*** Extracted from telegram:", syslog.LOG_DEBUG, DEBUG)
                mf.syslog_trace(f"    {telegram}", syslog.LOG_DEBUG, DEBUG)
                pass

    return f"{electra1in}, {electra2in}, {powerin}, {electra1out}, {electra2out}, {powerout}, {tarif}, {swits}"


# noinspection PyUnresolvedReferences
def gettelegram():
    """Fetch a telegram from the serialport."""
    global PORT
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
            # line = "".join(iter(lambda: PORT.read(1), delim)).strip()
            line = str(PORT.readline().strip(), "utf-8")
            if line == "!":
                abort = 1
            if line != "":
                telegram.append(line)
        except serial.SerialException:
            mf.syslog_trace("*** Serialport read error:", syslog.LOG_CRIT, DEBUG)
            mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
            abort = 2
        except UnicodeDecodeError:
            mf.syslog_trace("*** Unicode Decode error:", syslog.LOG_CRIT, DEBUG)
            mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
            abort = 2

        loops2go = loops2go - 1
        if loops2go < 0:
            abort = 3

    # test for correct start of telegram
    if telegram[0][0] != "/":
        abort = 2

    if abort == 1:
        with open("/tmp/kamstrup.raw", "w") as output_file:
            for line in telegram:
                output_file.write(f"{line}\n")

    # Return codes:
    # abort == 1 indicates a successful read
    # abort == 2 means that a serial port read/write error occurred
    # abort == 3 no valid data after several attempts
    return telegram, abort


def do_add_to_database(result, fdatabase, sql_cmd):
    """Commit the results to the database."""
    # Get the time and date in human-readable form and UN*X-epoch...
    conn = None
    cursor = None
    dt_format = "%Y-%m-%d %H:%M:%S"
    out_date = dt.datetime.now()  # time.strftime('%Y-%m-%dT%H:%M:%S')
    out_epoch = int(out_date.timestamp())
    results = (out_date.strftime(dt_format),
               out_epoch,
               result[0],
               result[1],
               result[2],
               result[3],
               result[4],
               result[5],
               result[6],
               result[7],
               )
    mf.syslog_trace(f"   @: {out_date.strftime(dt_format)}", False, DEBUG)
    mf.syslog_trace(f"    : {results}", False, DEBUG)

    err_flag = True
    while err_flag:
        try:
            conn = create_db_connection(fdatabase)
            cursor = conn.cursor()
            cursor.execute(sql_cmd, results)
            cursor.close()
            conn.commit()
            conn.close()
            err_flag = False
        except sqlite3.OperationalError:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


def create_db_connection(database_file):
    """
    Create a database connection to the SQLite3 database specified
    by database_file.
    """
    consql = None
    mf.syslog_trace(f"Connecting to: {database_file}", False, DEBUG)
    try:
        consql = sqlite3.connect(database_file, timeout=9000)
        # if consql:    # dB initialised succesfully -> get a cursor on the dB
        #                                               and run a test.
        #  cursql = consql.cursor()
        #  cursql.execute("SELECT sqlite_version()")
        #  versql = cursql.fetchone()
        #  cursql.close()
        #  logtext = f"Attached to SQLite3 server : {versql}"
        #  syslog.syslog(syslog.LOG_INFO, logtext)
        return consql
    except sqlite3.Error:
        mf.syslog_trace("Unexpected SQLite3 error when connecting to server.",
                        syslog.LOG_CRIT,
                        DEBUG,
                        )
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
    # initialise logging
    syslog.openlog(
        ident=f'{MYAPP}.{MYID.split(".")[0]}', facility=syslog.LOG_LOCAL0
    )

    # noinspection PyUnresolvedReferences
    PORT = serial.Serial()  # pylint: disable=C0103
    PORT.baudrate = 9600
    # noinspection PyUnresolvedReferences
    PORT.bytesize = serial.SEVENBITS
    # noinspection PyUnresolvedReferences
    PORT.parity = serial.PARITY_EVEN
    # noinspection PyUnresolvedReferences
    PORT.stopbits = serial.STOPBITS_ONE
    PORT.xonxoff = 1
    PORT.rtscts = 0
    PORT.dsrdtr = 0
    PORT.timeout = 15
    PORT.port = "/dev/ttyUSB0"

    if OPTION.debug:
        DEBUG = True
        mf.syslog_trace("Debug-mode started.", syslog.LOG_DEBUG, DEBUG)
        print("Use <Ctrl>+C to stop.")

    # OPTION.start only executes this next line, we don't need to test for it.
    main()

    print("And it's goodnight from him")
