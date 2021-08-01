#!/usr/bin/python3

import argparse
import datetime as dt
import os
import time
import traceback

# import sys

import libkamstrup as kl
import libzappi as zl


# import time
DEBUG = False

# constants
HERE = os.path.realpath(__file__).split("/")
# runlist id :
MYID = HERE[-1]
# app_name :
MYAPP = HERE[-3]
MYROOT = "/".join(HERE[0:-3])
# host_name :
NODE = os.uname()[1]

CONFIG_FILE = os.environ["HOME"] + "/.config/kamstrup/key.ini"

OPTION = ""


def store_data(data_tuple):
    """
    ...
    """
    global DEBUG
    global OPTION
    print("")
    data_lbls = data_tuple[0]
    importd = data_tuple[1]  # imp = P1 totaliser import
    opwekking = data_tuple[2]  # gep; PV production
    green = data_tuple[3]  # gen; own use
    exportd = data_tuple[4]  # exp = P1 totaliser export
    h1b = data_tuple[5]  # h1b = EV (imported)
    h1d = data_tuple[6]  # h1d = EV (from PV)
    utc_dt = data_tuple[7]
    #
    ev_usage = [x + y for x, y in zip(h1d, h1b)]
    iflux = kl.contract(importd, opwekking)
    oflux = kl.contract(kl.contract(exportd, h1d), h1b)
    own_usage = kl.distract(opwekking, exportd)

    own_usage = kl.distract(own_usage, h1b)
    # usage = kl.contract(own_usage, imprt)
    if OPTION.print or DEBUG:
        print("LBLS", data_lbls)
        print("TIME", utc_dt)
        print("imp", importd)
        print("exp", exportd)
        print("gep", opwekking)
        print("gen", green)
        print("h1b", h1b)
        print("h1d", h1d)
        print("")
        print("ofx", oflux)
        print("ifx", iflux)
        print("own", own_usage)
        print(".ev", ev_usage)

    """example data:
    LBLS ['07-28 01h', '07-28 02h', '07-28 03h', '07-28 04h', '07-28 05h', '07-28 06h', '07-28 07h', '07-28 08h', '07-28 09h', '07-28 10h', '07-28 11h', '07-28 12h', '07-28 13h']
    imp [0.189, 0.171, 0.152, 0.211, 0.071, 0.071, 0.17, 0.161, 0.128, 0.072, 0.072, 0.103, 0.053]
    exp [0.0, 0.0, 0.0, 0.001, 0.058, 0.23, 0.194, 0.148, 0.099, 0.169, 0.335, 0.701, 0.671]
    gen [0.007, 0.007, 0.007, 0.003, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    gep [0.0, 0.0, 0.0, 0.028, 0.223, 0.577, 1.313, 1.124, 1.365, 0.833, 0.84, 1.017, 1.183]
    h1d [0.0, 0.0, 0.0, 0.0, 0.0, 0.233, 1.032, 0.826, 1.111, 0.537, 0.29, 0.0, 0.0]
    """


def main():
    """
    This is the main loop
    """
    global OPTION

    if OPTION.day:
        store_data(myenergi.fetch_data(OPTION.day))
    if OPTION.status:
        zappi_status = myenergi.get_status(
            f"cgi-jstatus-Z{myenergi.zappi_serial}"
        )
        for k in zappi_status["zappi"][0]:
            print(f"{k}\t::  {zappi_status['zappi'][0][k]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch data from remote myenergi server."
    )
    parser.add_argument(
        "--day",
        type=str,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--iso",
        type=str,
        help="Fetch zappi data for a date in the ISO-format <YYYY-MM-DD>",
    )
    parser.add_argument(
        "--ymd",
        type=str,
        help="Fetch zappi data for a date in the sensible format <YYYY-MM-DD>",
    )
    parser.add_argument(
        "--dmy",
        type=str,
        help="Fetch zappi data for a date in the reasonable format <DD-MM-YYYY>",
    )
    parser.add_argument(
        "--mdy",
        type=str,
        help="Fetch zappi data for a date in the idiotic format <MM-DD-YYYY>",
    )
    parser.add_argument(
        "-p", "--print", action="store_true", help="Output data to stdout."
    )
    parser.add_argument(
        "-s",
        "--status",
        action="store_true",
        help="Display zappi current state",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="debug",
    )

    OPTION = parser.parse_args()
    if OPTION.print or DEBUG:
        print("Options passed: ", OPTION)
    if OPTION.iso:
        OPTION.day = dt.datetime.strptime(OPTION.iso, "%Y-%m-%d")
    if OPTION.ymd:
        OPTION.day = dt.datetime.strptime(OPTION.ymd, "%Y-%m-%d")
    if OPTION.dmy:
        OPTION.day = dt.datetime.strptime(OPTION.dmy, "%d-%m-%Y")
    if OPTION.mdy:
        OPTION.day = dt.datetime.strptime(OPTION.mdy, "%m-%d-%Y")
    if not OPTION.day:
        OPTION.day = dt.datetime.today()
    OPTION.day = OPTION.day.date()
    if OPTION.debug:
        DEBUG = True
    if OPTION.print or DEBUG:
        print("Options parsed: ", OPTION)
    # Initialise object and connect to myenergi server
    myenergi = zl.Myenergi(CONFIG_FILE, debug=DEBUG)
    main()
