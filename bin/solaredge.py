#!/usr/bin/env python3

"""
Communicate with the SolarEdge API to fetch energy production data.

- produced energy

Store the data in a sqlite3 database.
"""

import argparse
import configparser
import datetime as dt
import os
import sqlite3
import syslog
import time
import traceback

import libsolaredge as solaredge
import mausy5043funcs.fileops3 as mf
import mausy5043libs.libsignals3 as ml

parser = argparse.ArgumentParser(description="Execute the portal daemon.")
parser_group = parser.add_mutually_exclusive_group(required=True)
parser_group.add_argument('--start', action='store_true', help='start the daemon as a service')
parser_group.add_argument('--debug', action='store_true', help='start the daemon in debugging mode')
OPTION = parser.parse_args()

# constants
DEBUG = False
HERE = os.path.realpath(__file__).split('/')
# runlist id :
MYID = HERE[-1]
# app_name :
MYAPP = HERE[-3]
MYROOT = "/".join(HERE[0:-3])
# host_name :
NODE = os.uname()[1]

# example values:
# HERE: ['', 'home', 'pi', 'kamstrupd', 'bin', 'solaredge.py']
# MYID: 'solaredge.py
# MYAPP: kamstrupd
# MYROOT: /home/pi
# NODE: rbelec

API_SE = solaredge.Solaredge('0')


def main():
    """Execute main loop."""
    global API_SE
    killer = ml.GracefulKiller()
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
    # samples_averaged = iniconf.getint(MYID, 'samplespercycle') * iniconf.getint(MYID, 'cycles')
    sample_time = report_time / iniconf.getint(MYID, 'samplespercycle')
    data = []  # noqa

    test_db_connection(fdatabase)

    API_SE = solaredge.Solaredge(api_key)
    site_list = []
    pause_time = time.time()
    while not killer.kill_now:
        if time.time() > pause_time:
            start_time = time.time()
            if not site_list:
                try:
                    site_list = API_SE.get_list()['sites']['site']
                except Exception:  # noqa
                    mf.syslog_trace("Error connecting to SolarEdge", syslog.LOG_CRIT, DEBUG)
                    mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
                    site_list = []
                    pass

            if site_list:
                try:
                    start_time = time.time()
                    data = do_work(site_list)
                    if data:
                        mf.syslog_trace(f"Data to add : {data}", False, DEBUG)
                        do_add_to_database(data, fdatabase, sqlcmd)
                except Exception:  # noqa
                    mf.syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
                    mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
                    raise

            pause_time = (sample_time
                          - (time.time() - start_time)
                          - (start_time % sample_time)
                          + time.time())
            if pause_time > 0:
                mf.syslog_trace(f"Waiting  : {pause_time - time.time():.1f}s", False, DEBUG)
                mf.syslog_trace("................................", False, DEBUG)
                # time.sleep(pause_time)
            else:
                mf.syslog_trace(f"Behind   : {pause_time - time.time():.1f}s", False, DEBUG)
                mf.syslog_trace("................................", False, DEBUG)
        else:
            time.sleep(1.0)


def do_work(site_list):
    """Extract the data from the dict(s)."""
    global API_SE
    dt_format = '%Y-%m-%d %H:%M:%S'
    data_list = list()
    data_dict = dict()

    for site in site_list:
        site_id = site['id']
        try:
            data_dict = API_SE.get_overview(site_id)['overview']
        except Exception:  # noqa
            mf.syslog_trace("Request was unsuccesful.", syslog.LOG_WARNING, DEBUG)
            mf.syslog_trace(traceback.format_exc(), syslog.LOG_WARNING, DEBUG)
            mf.syslog_trace("Maybe next time...", syslog.LOG_WARNING, DEBUG)

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
        except KeyError:
            mf.syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
            mf.syslog_trace(f"site: {site_id}", syslog.LOG_CRIT, DEBUG)
            mf.syslog_trace(f"data: {data_dict}", syslog.LOG_CRIT, DEBUG)
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
    # initialise logging
    syslog.openlog(ident=f'{MYAPP}.{MYID.split(".")[0]}', facility=syslog.LOG_LOCAL0)

    if OPTION.debug:
        DEBUG = True
        mf.syslog_trace("Debug-mode started.", syslog.LOG_DEBUG, DEBUG)
        print("Use <Ctrl>+C to stop.")

    # OPTION.start only executes this next line, we don't need to test for it.
    main()

    print("And it's goodnight from him")
