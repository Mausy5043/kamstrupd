#!/usr/bin/env python3

"""Create multi-year graphs"""

import os
from datetime import datetime as dt

# noinspection PyUnresolvedReferences
import libkamstrup as kl
import matplotlib.pyplot as plt
import numpy as np

DATABASE = os.environ['HOME'] + "/.sqlite3/electriciteit.sqlite3"
OPTION = ''


def fetch_last_months():
    """
      ...
      """
    global DATABASE
    config = kl.add_time_line({'grouping': '%Y-%m',
                               'period': 61,
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


# noinspection SpellCheckingInspection
def plot_graph(output_file, data_tuple, plot_title):
    """
      Create the graph
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
    grph_lbls, total_use, total_out = kl.build_arrays44(data_lbls, usage, exprt)
    """
    --- Start debugging:
    np.set_printoptions(precision=3)
    yr = 6
    print("data_lbls: ", np.shape(data_lbls), data_lbls[-5:])
    print(" ")
    print("opwekking: ", np.shape(opwekking), opwekking[-5:])
    print(" ")
    print("export_hi: ", np.shape(export_hi), export_hi[-5:])
    print("export_lo: ", np.shape(export_lo), export_lo[-5:])
    print("exprt    : ", np.shape(exprt), exprt[-5:])
    print(" ")
    print("import_hi: ", np.shape(import_hi), import_hi[-5:])
    print("import_lo: ", np.shape(import_lo), import_lo[-5:])
    print("imprt    : ", np.shape(imprt), imprt[-5:])
    print(" ")
    print("own_usage: ", np.shape(own_usage), own_usage[-5:])
    print("usage    : ", np.shape(usage), usage[-5:])
    print(" ")
    print(" ")
    print("grph_lbls: ", np.shape(grph_lbls), grph_lbls)
    print(" ")
    print("total_use: ", np.shape(total_use), total_use[yr])
    print(" ")
    print("total_out: ", np.shape(total_out), total_out[yr])
    --- End debugging.
    """
    # Set the bar width
    bars_width = 0.9
    bar_width = bars_width / len(grph_lbls[0])
    # Set the color alpha
    ahpla = 1 - (1 / (len(grph_lbls[0]) + 1) * len(grph_lbls[0]))
    # positions of the left bar-boundaries
    tick_pos = np.arange(1, len(grph_lbls[1]) + 1) - (bars_width / 2)

    # Create the general plot and the bar
    plt.rc('font', size=6.5)
    dummy, ax1 = plt.subplots(1, figsize=(10, 3.5))

    # Create a bar plot usage
    for idx in range(0, len(grph_lbls[0])):
        ax1.bar(tick_pos + (idx * bar_width), total_use[idx],
                width=bar_width,
                label=grph_lbls[0][idx],
                alpha=ahpla + (idx * ahpla),
                color='b',
                align='edge'
                )
        # Create a bar plot of production
        ax1.bar(tick_pos + (idx * bar_width), [-1 * i for i in total_out[idx]],
                width=bar_width,
                alpha=ahpla + (idx * ahpla),
                color='r',
                align='edge'
                )

    # Set Axes stuff
    ax1.set_ylabel("[kWh]")
    ax1.set_xlabel("Datetime")
    ax1.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
    ax1.axhline(y=0, color='k')
    ax1.axvline(x=0, color='k')
    # Set plot stuff
    plt.xticks(tick_pos + (bars_width / 2), grph_lbls[1])
    plt.title(f'{plot_title}')
    plt.legend(loc='upper left', ncol=6, framealpha=0.2)
    # Fit every nicely
    plt.xlim([min(tick_pos) - (bars_width / 2), max(tick_pos) + (bars_width / 2 * 3)])
    plt.tight_layout()
    plt.savefig(fname=f'{output_file}', format='png')


def main():
    """
      This is the main loop
      """
    global OPTION
    OPTION = kl.get_cli_params(1)

    if OPTION in ['-m', '-M', '-y', '-Y', '-a', '-A']:
        plot_graph('/tmp/kamstrupd/site/img/kam_vs_month.png',
                   fetch_last_months(),
                   f"Stroomverbruik/levering per maand afgelopen jaren ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
                   )


if __name__ == "__main__":
    main()
