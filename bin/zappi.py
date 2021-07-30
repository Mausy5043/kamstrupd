#!/usr/bin/python3

import argparse
import datetime
import os

import libkamstrup as kl
import libzappi as zl
import matplotlib.pyplot as plt

from datetime import datetime as dt


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
    zdst = int(zappi_status["zappi"][0]["dst"])

    time_dict = {"hours": hours_to_fetch + 2}
    time_delta = datetime.timedelta(**time_dict)
    time_obj = datetime.datetime.now() - time_delta

    # ztime[0] -= hours_to_fetch
    # if ztime[0] < 0:
    #     ztime[0] += 24
    #     zdate[0] -= 1
    #     if zdate[1] < 1:
    #         zdate[1] += 12
    #         zdate[2] -= 1
    # zdate = int2str(zdate)
    # ztime = int2str(ztime)

    zappi_data = myenergi.get_status(
        f"cgi-jdayhour-Z{myenergi.zappi_serial}-{time_obj.year}-{time_obj.month}-{time_obj.day}-{time_obj.hour}"
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
    h1b = list()
    for key, value in enumerate(zappi_data[f"U{myenergi.zappi_serial}"]):
        block_values = myenergi.trans_data_block(value, zdst)
        data_lbls.append(block_values[0])
        imp.append(block_values[1])
        gep.append(block_values[2])
        gen.append(block_values[3])
        exp.append(block_values[4])
        h1b.append(block_values[6])
    return data_lbls, imp, gep, gen, exp, h1d, h1b


def plot_graph(output_file, data_tuple, plot_title, show_data=0):
    """
    ...
    """
    data_lbls = data_tuple[0]
    importd = data_tuple[1]  # imp = P1 totaliser import
    opwekking = data_tuple[2]  # gep; PV production
    green = data_tuple[3]  # gen; own use
    exportd = data_tuple[4]  # exp = P1 totaliser export
    h1d = data_tuple[5]  # h1d = EV (from PV)
    h1b = data_tuple[6]  # h1d = EV (imported)
    #
    imprt = importd
    exprt = exportd
    ev_usage = h1d + h1b
    iflux = kl.contract(imprt, opwekking)
    oflux = kl.contract(exprt, h1d)
    own_usage = kl.distract(iflux, exprt)
    # own_usage = kl.distract(opwekking, exprt)
    # usage = kl.contract(own_usage, imprt)
    print("LBLS", data_lbls)
    print("imp", importd)
    print("exp", exportd)
    print("gep", opwekking)
    print("gen", green)
    print("h1d", h1d)
    print("h1b", h1b)
    print("own", own_usage)


    # Set the bar width
    bar_width = 0.75
    # Set the color alpha
    ahpla = 0.7
    # positions of the left bar-boundaries
    tick_pos = list(range(1, len(data_lbls) + 1))

    # Create the general plot and the bar
    plt.rc("font", size=6.5)
    dummy, ax1 = plt.subplots(1, figsize=(10, 3.5))
    col_import = "red"
    col_export = "blue"
    col_ev = "yellow"
    col_usage = "green"

    """example data:
    LBLS ['07-28 01h', '07-28 02h', '07-28 03h', '07-28 04h', '07-28 05h', '07-28 06h', '07-28 07h', '07-28 08h', '07-28 09h', '07-28 10h', '07-28 11h', '07-28 12h', '07-28 13h']
    imp [0.189, 0.171, 0.152, 0.211, 0.071, 0.071, 0.17, 0.161, 0.128, 0.072, 0.072, 0.103, 0.053]
    exp [0.0, 0.0, 0.0, 0.001, 0.058, 0.23, 0.194, 0.148, 0.099, 0.169, 0.335, 0.701, 0.671]
    gen [0.007, 0.007, 0.007, 0.003, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    gep [0.0, 0.0, 0.0, 0.028, 0.223, 0.577, 1.313, 1.124, 1.365, 0.833, 0.84, 1.017, 1.183]
    h1d [0.0, 0.0, 0.0, 0.0, 0.0, 0.233, 1.032, 0.826, 1.111, 0.537, 0.29, 0.0, 0.0]
    """

    # Create a bar plot of importd
    ax1.bar(
        tick_pos,
        importd,
        width=bar_width,
        label="Inkoop",
        alpha=ahpla,
        color=col_import,
        align="center",
        bottom=own_usage,
    )
    # Create a bar plot of import_hi
    ax1.bar(
        tick_pos,
        own_usage,
        width=bar_width,
        label="Eigen Gebruik",
        alpha=ahpla,
        color=col_usage,
        align="center",
    )
    # Create a bar plot of own_usage
    ax1.bar(
        tick_pos,
        ev_usage,
        width=bar_width,
        label="EV",
        alpha=ahpla * 0.7,
        color=col_ev,
        align="center",
    )

    # Exports hang below the y-axis
    # Create a bar plot of exportd
    ax1.bar(
        tick_pos,
        [-1 * i for i in exportd],
        width=bar_width,
        label="Verkoop",
        alpha=ahpla,
        color=col_export,
        align="center",
    )

    # Set Axes stuff
    ax1.set_ylabel("[kWh]")

    ax1.set_xlabel("Datetime")
    ax1.grid(
        which="major", axis="y", color="k", linestyle="--", linewidth=0.5
    )
    ax1.axhline(y=0, color="k")
    ax1.axvline(x=0, color="k")
    # Set plot stuff
    plt.xticks(tick_pos, data_lbls, rotation=-60)
    plt.title(f"{plot_title}")
    plt.legend(loc="upper left", ncol=5, framealpha=0.2)
    # Fit every nicely
    plt.xlim([min(tick_pos) - bar_width, max(tick_pos) + bar_width])
    plt.tight_layout()
    plt.savefig(fname=f"{output_file}", format="png")


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
    # Initialise object and connect to myenergi server
    myenergi = zl.Myenergi(CONFIG_FILE, debug=DEBUG)
    main()
