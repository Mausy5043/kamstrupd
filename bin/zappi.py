#!/usr/bin/python3

import argparse
import datetime as dt
import os

import libkamstrup as kl
import libzappi as zl
import matplotlib.pyplot as plt


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


# def fetch_last_day(hours_to_fetch):
#     # zappi_status = myenergi.get_status(
#     #     f"cgi-jstatus-Z{myenergi.zappi_serial}"
#     # )
#     # zdate = str2int(zappi_status["zappi"][0]["dat"].split("-"))
#     # ztime = str2int(zappi_status["zappi"][0]["tim"].split(":"))
#     # zdst = int(zappi_status["zappi"][0]["dst"])

#     # time_dict = {"hours": hours_to_fetch + 2}
#     # time_delta = datetime.timedelta(**time_dict)
#     # time_obj = datetime.datetime.now() - time_delta

#     # ztime[0] -= hours_to_fetch
#     # if ztime[0] < 0:
#     #     ztime[0] += 24
#     #     zdate[0] -= 1
#     #     if zdate[1] < 1:
#     #         zdate[1] += 12
#     #         zdate[2] -= 1
#     # zdate = int2str(zdate)
#     # ztime = int2str(ztime)

#     zappi_data = myenergi.get_status(
#         f"cgi-jdayhour-Z{myenergi.zappi_serial}-{time_obj.year}-{time_obj.month}-{time_obj.day}-{time_obj.hour}"
#     )
#     # for key, value in enumerate(zappi_status["zappi"][0]):
#     #     print(key, value, zappi_status["zappi"][0][value])
#     print("")
#     data_lbls = list()
#     imp = list()
#     gep = list()
#     gen = list()
#     exp = list()
#     h1b = list()
#     h1d = list()
#     for key, value in enumerate(zappi_data[f"U{myenergi.zappi_serial}"]):
#         block_values = myenergi.trans_data_block(value, zdst)
#         data_lbls.append(block_values[0])
#         imp.append(block_values[1])
#         gep.append(block_values[2])
#         gen.append(block_values[3])
#         exp.append(block_values[4])
#         h1b.append(block_values[5])
#         h1d.append(block_values[6])
#     return data_lbls, imp, gep, gen, exp, h1b, h1d


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

    # if OPTION.hours:
    #     plot_graph(
    #         "/tmp/kamstrupd/site/img/zap_pastday.png",
    #         fetch_last_day(OPTION.hours),
    #         f"Energietrend per uur afgelopen dagen ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
    #     )
    if OPTION.day:
        plot_graph(
            "/tmp/kamstrupd/site/img/zap_pastday.png",
            myenergi.fetch_data(OPTION.day),
            f"Energietrend per uur afgelopen dagen ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
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
    # parser.add_argument(
    #     "-d", "--days", type=int, help="create day-trend for last <DAYS> days"
    # )

    parser.add_argument(
        "--day",
        type=str,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--iso",
        type=str,
        help="Fetch zappi data for a date <YYYY-MM-DD>",
    )
    parser.add_argument(
        "--ymd",
        type=str,
        help="Fetch zappi data for a date <YYYY-MM-DD>",
    )
    parser.add_argument(
        "--dmy",
        type=str,
        help="Fetch zappi data for a date <YYYY-MM-DD>",
    )
    parser.add_argument(
        "--mdy",
        type=str,
        help="Fetch zappi data for a date <YYYY-MM-DD>",
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

    # if OPTION.hours == 0:
    #     OPTION.hours = 5
    # if OPTION.days == 0:
    #     OPTION.days = 5
    # Initialise object and connect to myenergi server
    myenergi = zl.Myenergi(CONFIG_FILE, debug=DEBUG)
    main()
