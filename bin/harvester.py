#!/usr/bin/env python3

import argparse
import datetime as dt
import os

import pandas as pd

import libzappi as zl

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
    df = pd.DataFrame(data_tuple[8])
    print(type(df))

    if OPTION.print or DEBUG:
        print(df)
        print("")
        """example data:
                                         imp    exp    gep  gen  h1b    h1d                    dt_lcl
            dt_lcl
            2021-07-19 02:00:00+02:00  0.220  0.000  0.000  0.0  0.0  0.000 2021-07-19 02:00:00+02:00
            2021-07-19 03:00:00+02:00  0.226  0.000  0.000  0.0  0.0  0.000 2021-07-19 03:00:00+02:00
            2021-07-19 04:00:00+02:00  0.221  0.000  0.000  0.0  0.0  0.000 2021-07-19 04:00:00+02:00
            2021-07-19 05:00:00+02:00  0.201  0.000  0.000  0.0  0.0  0.000 2021-07-19 05:00:00+02:00
        """


def main():
    """
    This is the main loop
    """
    global OPTION

    if OPTION.day:
        store_data(myenergi.fetch_data(OPTION.day))
    if OPTION.status:
        zappi_status = myenergi.get_status(f"cgi-jstatus-Z{myenergi.zappi_serial}")
        for k in zappi_status["zappi"][0]:
            print(f"{k}\t::  {zappi_status['zappi'][0][k]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch data from remote myenergi server.")
    parser.add_argument("--day",
                        type=str,
                        help=argparse.SUPPRESS,
                        )
    parser.add_argument("--iso",
                        type=str,
                        help="Fetch zappi data for a date in the ISO-format <YYYY-MM-DD>",
                        )
    parser.add_argument("--ymd",
                        type=str,
                        help="Fetch zappi data for a date in the sensible format <YYYY-MM-DD>",
                        )
    parser.add_argument("--dmy",
                        type=str,
                        help="Fetch zappi data for a date in the reasonable format <DD-MM-YYYY>",
                        )
    parser.add_argument("--mdy",
                        type=str,
                        help="Fetch zappi data for a date in the idiotic format <MM-DD-YYYY>",
                        )
    parser.add_argument("-p",
                        "--print",
                        action="store_true",
                        help="Output data to stdout."
                        )
    parser.add_argument("-s",
                        "--status",
                        action="store_true",
                        help="Display zappi current state",
                        )
    parser.add_argument("-d",
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
