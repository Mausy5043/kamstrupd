#!/usr/bin/env python3

import argparse
import datetime as dt
import os

import matplotlib.pyplot as plt

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


def plot_graph(output_file, data_tuple, plot_title):
    """
    ...
    """
    global DEBUG
    global OPTION
    print("")
    data_lbls = data_tuple[0]
    importd = data_tuple[1]  # imp = P1 totaliser import
    opwekking = data_tuple[2]  # gep; PV production
    green = data_tuple[3]  # gen; PV own use
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

    # Create a bar plot of importd
    ax1.bar(tick_pos,
            importd,
            width=bar_width,
            label="Inkoop",
            alpha=ahpla,
            color=col_import,
            align="center",
            bottom=own_usage,
            )
    # Create a bar plot of import_hi
    ax1.bar(tick_pos,
            own_usage,
            width=bar_width,
            label="Eigen Gebruik",
            alpha=ahpla,
            color=col_usage,
            align="center",
            )
    # Create a bar plot of own_usage
    ax1.bar(tick_pos,
            ev_usage,
            width=bar_width,
            label="EV",
            alpha=ahpla * 0.9,
            color=col_ev,
            align="center",
            )

    # Exports hang below the y-axis
    # Create a bar plot of exportd
    ax1.bar(tick_pos,
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
    ax1.grid(which="major",
             axis="y",
             color="k",
             linestyle="--",
             linewidth=0.5
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

    # if OPTION.hours:
    #     plot_graph("/tmp/kamstrupd/site/img/zap_pastday.png",
    #         fetch_last_day(OPTION.hours),
    #         f"Energietrend per uur afgelopen dagen ({dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')})",
    #     )
    if OPTION.day:
        plot_graph("/tmp/kamstrupd/site/img/zap_pastday.png",
                   myenergi.fetch_data(OPTION.day),
                   f"Energietrend per uur afgelopen dagen ({dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')})"
                   )
    # if OPTION.days:
    #     plot_graph("/tmp/kamstrupd/site/img/kam_pastmonth.png",
    #         fetch_last_month(OPTION.days),
    #         f"Energietrend per dag afgelopen maand ({dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')})",
    #     )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a trendgraph")
    parser.add_argument("-hr",
                        "--hours",
                        type=int,
                        help="create hour-trend for last <HOURS> hours",
                        )
    # parser.add_argument("-d",
    # "--days",
    # type=int,
    # help="create day-trend for last <DAYS> days"
    # )

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

    # if OPTION.hours == 0:
    #     OPTION.hours = 5
    # if OPTION.days == 0:
    #     OPTION.days = 5
    # Initialise object and connect to myenergi server
    myenergi = zl.Myenergi(CONFIG_FILE, debug=DEBUG)
    main()
