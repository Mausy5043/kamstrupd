#!/usr/bin/env python3

"""Create trendbargraphs for various periods of electricity use and production."""

import os
from datetime import datetime as dt

# noinspection PyUnresolvedReferences
import libkamstrup as kl
import matplotlib.pyplot as plt
import numpy as np

DATABASE = os.environ['HOME'] + "/.sqlite3/electriciteit.sqlite3"
OPTION = ''


def fetch_last_day():
    """
      ...
      """
    global DATABASE
    config = kl.add_time_line({'grouping': '%m-%d %Hh',
                               'period': 50,
                               'timeframe': 'hour',
                               'database': DATABASE,
                               'table': 'production'
                               })

    opwekking, prod_lbls = kl.get_historic_data(config, telwerk='energy')
    config['table'] = 'kamstrup'
    import_lo, data_lbls = kl.get_historic_data(config, telwerk='T1in')
    import_hi, data_lbls = kl.get_historic_data(config, telwerk='T2in')
    export_lo, data_lbls = kl.get_historic_data(config, telwerk='T1out')
    export_hi, data_lbls = kl.get_historic_data(config, telwerk='T2out')
    # production data may not yet have caught up to the current hour
    if not (prod_lbls[-1] == data_lbls[-1]):
        opwekking = opwekking[:-1]
        np.append(opwekking, 0.0)
    return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def fetch_last_month():
    """
      ...
      """
    global DATABASE
    config = kl.add_time_line({'grouping': '%m-%d',
                               'period': 50,
                               'timeframe': 'day',
                               'database': DATABASE,
                               'table': 'production'
                               })
    opwekking, prod_lbls = kl.get_historic_data(config, telwerk='energy')
    config['table'] = 'kamstrup'
    import_lo, data_lbls = kl.get_historic_data(config, telwerk='T1in')
    import_hi, data_lbls = kl.get_historic_data(config, telwerk='T2in')
    export_lo, data_lbls = kl.get_historic_data(config, telwerk='T1out')
    export_hi, data_lbls = kl.get_historic_data(config, telwerk='T2out')
    # production data may not yet have caught up to the current hour
    if not (prod_lbls[-1] == data_lbls[-1]):
        opwekking = opwekking[:-1]
        np.append(opwekking, 0.0)
    return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def fetch_last_year():
    """
      ...
      """
    global DATABASE
    config = kl.add_time_line({'grouping': '%Y-%m',
                               'period': 38,
                               'timeframe': 'month',
                               'database': DATABASE,
                               'table': 'production'
                               })
    opwekking, prod_lbls = kl.get_historic_data(config, telwerk='energy', from_start_of_year=True)
    config['table'] = 'kamstrup'
    import_lo, data_lbls = kl.get_historic_data(config, telwerk='T1in', from_start_of_year=True)
    import_hi, data_lbls = kl.get_historic_data(config, telwerk='T2in', from_start_of_year=True)
    export_lo, data_lbls = kl.get_historic_data(config, telwerk='T1out', from_start_of_year=True)
    export_hi, data_lbls = kl.get_historic_data(config, telwerk='T2out', from_start_of_year=True)
    # production data may not yet have caught up to the current hour
    if not (prod_lbls[-1] == data_lbls[-1]):
        opwekking = opwekking[:-1]
        np.append(opwekking, 0.0)
    return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def fetch_last_years():
    """
      ...
      """
    global DATABASE
    config = kl.add_time_line({'grouping': '%Y',
                               'period': 6,
                               'timeframe': 'year',
                               'database': DATABASE,
                               'table': 'production'
                               })
    opwekking, prod_lbls = kl.get_historic_data(config, telwerk='energy', from_start_of_year=True)
    config['table'] = 'kamstrup'
    import_lo, data_lbls = kl.get_historic_data(config, telwerk='T1in', from_start_of_year=True)
    import_hi, data_lbls = kl.get_historic_data(config, telwerk='T2in', from_start_of_year=True)
    export_lo, data_lbls = kl.get_historic_data(config, telwerk='T1out', from_start_of_year=True)
    export_hi, data_lbls = kl.get_historic_data(config, telwerk='T2out', from_start_of_year=True)
    # production data may not yet have caught up to the current hour
    if not (prod_lbls[-1] == data_lbls[-1]):
        opwekking = opwekking[:-1]
        np.append(opwekking, 0.0)
    return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def plot_graph(output_file, data_tuple, plot_title, show_data=0):
    """
      ...
      """
    data_lbls = data_tuple[0]
    import_lo = data_tuple[1]
    import_hi = data_tuple[2]
    opwekking = data_tuple[3]
    export_lo = data_tuple[4]
    export_hi = data_tuple[5]
    imprt = kl.contract(import_lo, import_hi)
    exprt = kl.contract(export_lo, export_hi)
    own_usage = kl.distract(opwekking, exprt)
    usage = kl.contract(own_usage, imprt)
    btm_hi = kl.contract(import_lo, own_usage)
    """
    --- Start debugging:
    np.set_printoptions(precision=3)
    print("data_lbls: ", np.size(data_lbls), data_lbls[-5:])
    print(" ")
    print("opwekking: ", np.size(opwekking), opwekking[-5:])
    print(" ")
    print("export_hi: ", np.size(export_hi), export_hi[-5:])
    print("export_lo: ", np.size(export_lo), export_lo[-5:])
    print("exprt    : ", np.size(exprt), exprt[-5:])
    print(" ")
    print("import_hi: ", np.size(import_hi), import_hi[-5:])
    print("import_lo: ", np.size(import_lo), import_lo[-5:])
    print("imprt    : ", np.size(imprt), imprt[-5:])
    print(" ")
    print("own_usage: ", np.size(own_usage), own_usage[-5:])
    print("usage    : ", np.size(usage), usage[-5:])
    print(" ")
    print("btm_hi   : ", np.size(btm_hi), btm_hi[-5:])
    --- End debugging.
    """
    # Set the bar width
    bar_width = 0.75
    # Set the color alpha
    ahpla = 0.7
    # positions of the left bar-boundaries
    tick_pos = list(range(1, len(data_lbls) + 1))

    # Create the general plot and the bar
    plt.rc('font', size=6.5)
    dummy, ax1 = plt.subplots(1, figsize=(10, 3.5))

    # Create a bar plot of import_lo
    ax1.bar(tick_pos, import_hi,
            width=bar_width,
            label='Inkoop (normaal)',
            alpha=ahpla,
            color='orange',
            align='center',
            bottom=btm_hi  # [sum(i) for i in zip(import_lo, own_usage)]
            )
    # Create a bar plot of import_hi
    ax1.bar(tick_pos, import_lo,
            width=bar_width,
            label='Inkoop (dal)',
            alpha=ahpla,
            color='b',
            align='center',
            bottom=own_usage
            )
    # Create a bar plot of own_usage
    ax1.bar(tick_pos, own_usage,
            width=bar_width,
            label='Eigen gebruik',
            alpha=ahpla,
            color='g',
            align='center'
            )
    if show_data == 1:
        for i, v in enumerate(own_usage):
            ax1.text(tick_pos[i], 10, "{:7.3f}".format(v), {'ha': 'center', 'va': 'bottom'}, rotation=-90)
    if show_data == 2:
        for i, v in enumerate(usage):
            ax1.text(tick_pos[i], 500, "{:4.0f}".format(v), {'ha': 'center', 'va': 'bottom'}, fontsize=12)
    # Exports hang below the y-axis
    # Create a bar plot of export_lo
    ax1.bar(tick_pos, [-1 * i for i in export_lo],
            width=bar_width,
            label='Verkoop (dal)',
            alpha=ahpla,
            color='c',
            align='center'
            )
    # Create a bar plot of export_hi
    ax1.bar(tick_pos, [-1 * i for i in export_hi],
            width=bar_width,
            label='Verkoop (normaal)',
            alpha=ahpla,
            color='r',
            align='center',
            bottom=[-1 * i for i in export_lo]
            )
    if show_data == 1:
        for i, v in enumerate(exprt):
            ax1.text(tick_pos[i], -10, "{:7.3f}".format(v), {'ha': 'center', 'va': 'top'}, rotation=-90)
    if show_data == 2:
        for i, v in enumerate(exprt):
            ax1.text(tick_pos[i], -500, "{:4.0f}".format(v), {'ha': 'center', 'va': 'top'}, fontsize=12)

    # Set Axes stuff
    ax1.set_ylabel("[kWh]")
    if show_data == 0:
        y_lo = -1 * (max(exprt) + 1)
        y_hi = max(usage) + 1
        if y_lo > -1.5:
            y_lo = -1.5
        if y_hi < 1.5:
            y_hi = 1.5
        ax1.set_ylim([y_lo, y_hi])

    ax1.set_xlabel("Datetime")
    ax1.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
    ax1.axhline(y=0, color='k')
    ax1.axvline(x=0, color='k')
    # Set plot stuff
    plt.xticks(tick_pos, data_lbls, rotation=-60)
    plt.title(f'{plot_title}')
    plt.legend(loc='upper left', ncol=5, framealpha=0.2)
    # Fit every nicely
    plt.xlim([min(tick_pos) - bar_width, max(tick_pos) + bar_width])
    plt.tight_layout()
    plt.savefig(fname=f'{output_file}', format='png')


def main():
    """
      This is the main loop
      """
    global OPTION
    OPTION = kl.get_cli_params(1)

    if OPTION in ['-d', '-D', '-a', '-A']:
        plot_graph('/tmp/kamstrupd/site/img/kam_pastday.png',
                   fetch_last_day(),
                   f"Energietrend per uur afgelopen dagen ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
                   )

    if OPTION in ['-m', '-M', '-a', '-A']:
        plot_graph('/tmp/kamstrupd/site/img/kam_pastmonth.png',
                   fetch_last_month(),
                   f"Energietrend per dag afgelopen maand ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
                   )

    if OPTION in ['-y', '-Y', '-y1', '-Y1' '-a', '-A']:
        plot_graph('/tmp/kamstrupd/site/img/kam_pastyear.png',
                   fetch_last_year(),
                   f"Energietrend per maand afgelopen jaren ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
                   show_data=1
                   )

    if OPTION in ['-y', '-Y', '-y2', '-Y2' '-a', '-A']:
        plot_graph('/tmp/kamstrupd/site/img/kam_vs_year.png',
                   fetch_last_years(),
                   f"Energietrend per jaar afgelopen jaren ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
                   show_data=2
                   )


if __name__ == "__main__":
    main()
