#!/usr/bin/python3

import os

import libzappi as zl

import argparse
import sys
from datetime import datetime as dt

# noinspection PyUnresolvedReferences
import libkamstrup as kl

# import matplotlib.pyplot as plt
import numpy as np

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


def str2int(arr):
    for k, v in enumerate(arr):
        arr[k] = int(v)
    return arr


def int2str(arr):
    for k, v in enumerate(arr):
        arr[k] = str(v).zfill(2)
    return arr


def fetch_last_day(hours_to_fetch):
    zappi_status = myenergi.get_status(
        f"cgi-jstatus-Z{myenergi.zappi_serial}"
    )
    zdate = str2int(zappi_status["zappi"][0]["dat"].split("-"))
    ztime = str2int(zappi_status["zappi"][0]["tim"].split(":"))

    ztime[0] -= hours_to_fetch
    if ztime[0] < 0:
        ztime[0] += 24
        zdate[0] -= 1
        if zdate[1] < 1:
            zdate[1] += 12
            zdate[2] -= 1
    zdate = int2str(zdate)
    ztime = int2str(ztime)

    zappi_data = myenergi.get_status(
        f"cgi-jdayhour-Z{myenergi.zappi_serial}-{zdate[2]}-{zdate[1]}-{zdate[0]}-{ztime[0]}"
    )
    # for key, value in enumerate(zappi_status["zappi"][0]):
    #     print(key, value, zappi_status["zappi"][0][value])
    print("")
    data_lbls = list()
    imp = list()
    gep = list()
    gen = list()
    exp = list()
    h1d = list()
    for key, value in enumerate(zappi_data[f"U{myenergi.zappi_serial}"]):
        block_values = myenergi.trans_data_block(value)
        data_lbls.append(block_values[0])
        imp.append(block_values[1])
        gep.append(block_values[2])
        gen.append(block_values[3])
        exp.append(block_values[4])
        h1d.append(block_values[5])
    return data_lbls, imp, gep, gen, exp, h1d


def plot_graph(output_file, data_tuple, plot_title, show_data=0):
    """
    ...
    """
    data_lbls = data_tuple[0]
    importd = data_tuple[1]
    green = data_tuple[2]
    opwekking = data_tuple[3]
    exportd = data_tuple[4]
    h1d = data_tuple[5]
    # imprt = kl.contract(import_lo, import_hi)
    # exprt = kl.contract(export_lo, export_hi)
    # own_usage = kl.distract(opwekking, exprt)
    # usage = kl.contract(own_usage, imprt)
    # btm_hi = kl.contract(import_lo, own_usage)
    print("LBLS", data_lbls)
    print("imp", importd)
    print("exp", exportd)
    print("gen", opwekking)
    print("gep", green)
    print("h1d", h1d)


def main():
    """
    This is the main loop
    """
    global OPTION

    if OPTION.hours:
        plot_graph(
            "/tmp/kamstrupd/site/img/zap_pastday.png",
            fetch_last_day(OPTION.hours),
            f"Energietrend per uur afgelopen dagen ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
        )
    # if OPTION.days:
    #     plot_graph(
    #         "/tmp/kamstrupd/site/img/kam_pastmonth.png",
    #         fetch_last_month(OPTION.days),
    #         f"Energietrend per dag afgelopen maand ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
    #     )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a trendgraph")
    parser.add_argument(
        "-hr",
        "--hours",
        type=int,
        help="create hour-trend for last <HOURS> hours",
    )
    parser.add_argument(
        "-d", "--days", type=int, help="create day-trend for last <DAYS> days"
    )

    OPTION = parser.parse_args()
    if OPTION.hours == 0:
        OPTION.hours = 5
    if OPTION.days == 0:
        OPTION.days = 5
    # OPTION.hours = 5
    # Initialise object and connect to myenergi server
    myenergi = zl.Myenergi(CONFIG_FILE, debug=DEBUG)
    main()
