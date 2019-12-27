#!/usr/bin/env python3

"""."""


import os
import sqlite3 as s3
import sys

import matplotlib.pyplot as plt

DATABASE = os.environ['HOME'] + "/.sqlite3/electriciteit.sqlite3"

def get_cli_params(expected_amount):
    """Check for presence of a CLI parameter."""
    if len(sys.argv) != (expected_amount + 1):
        print(f"{expected_amount} arguments expected, {len(sys.argv) - 1} received.")
        sys.exit(0)
    return sys.argv[1]


def get_historic_data(grouping, period, timeframe, telwerk, from_start_of_year=False):
    """
    Fetch import data LO
    """
    ret_data = []
    ret_lbls = []
    if from_start_of_year:
        interval = f"datetime(datetime(\'now\', \'-{period} {timeframe}\'), \'start of year\')"
    else:
        interval = f"datetime(\'now\', \'-{period} {timeframe}\')"
    db_con = s3.connect(DATABASE)
    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(f"SELECT strftime('{grouping}',sample_time) as grouped, \
                     MAX({telwerk})-MIN({telwerk}), \
                     MIN(sample_epoch) as t \
                     FROM kamstrup \
                     WHERE (sample_time >= {interval}) \
                     GROUP BY grouped \
                     ORDER BY t ASC \
                     ;"
                    )
        db_data = db_cur.fetchall()

    for row in db_data:
        ret_data.append(row[1]/1000) # convert Wh to kWh
        ret_lbls.append(row[0])

    return ret_data[-period*12:], ret_lbls[-period*12:]


def get_opwekking(period, timeframe, from_start_of_year=False):
    """
    Fetch production data
    """
    if from_start_of_year: #bogus code
        timeframe+=1
    ret_data = [0] * period*12
    return ret_data


def fetch_last_months():
    """
    ...
    """
    import_lo, data_lbls = get_historic_data('%Y-%m', 5, 'year', 'T1in', from_start_of_year=True)
    import_hi, data_lbls = get_historic_data('%Y-%m', 5, 'year', 'T2in', from_start_of_year=True)
    export_lo, data_lbls = get_historic_data('%Y-%m', 5, 'year', 'T1out', from_start_of_year=True)
    export_hi, data_lbls = get_historic_data('%Y-%m', 5, 'year', 'T2out', from_start_of_year=True)
    opwekking = get_opwekking(5, 'year')
    return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def plot_graph(output_file, data_tuple, plot_title):
    """
    ...
    """
    data_lbls = data_tuple[0]
    import_lo = data_tuple[1]
    import_hi = data_tuple[2]
    opwekking = data_tuple[3]
    export_lo = data_tuple[4]
    export_hi = data_tuple[5]
    own_usage = [sum(x) for x in zip(opwekking, export_hi, export_lo)]
    total_use = [sum(x) for x in zip(own_usage, import_lo, import_hi)]
    total_out = [sum(x) for x in zip(export_lo, export_hi)]

    # Set the bar width
    bar_width = 0.75
    # Set the color alpha
    ahpla = 0.7
    # positions of the left bar-boundaries
    tick_pos = list(range(1, len(data_lbls)+1))

    #Create the general plot and the bar
    plt.rc('font', size=13)
    dummy, ax1 = plt.subplots(1, figsize=(20, 7))

    # Create a bar plot of import_lo
    ax1.bar(tick_pos, total_use,
            width=bar_width,
            label='Verbruik',
            alpha=ahpla,
            color='b',
            align='center'
            )
    # Create a bar plot of import_hi
    ax1.bar(tick_pos, [-1*i for i in total_out],
            width=bar_width,
            label='Export',
            alpha=ahpla,
            color='g',
            align='center'
            )

    # Set Axes stuff
    ax1.set_ylabel("[kWh]")
    ax1.set_xlabel("Datetime")
    ax1.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
    ax1.axhline(y=0, color='k')
    ax1.axvline(x=0, color='k')
    # Set plot stuff
    plt.xticks(tick_pos, data_lbls, rotation=-60)
    plt.title(f'{plot_title}')
    plt.legend(loc='upper left', ncol=5, framealpha=0.2)
    # Fit every nicely
    plt.xlim([min(tick_pos)-bar_width, max(tick_pos)+bar_width])
    plt.tight_layout()
    plt.savefig(fname=f'{output_file}', format='png')


def main():
    """
    This is the main loop
    """
    OPTION = get_cli_params(1)

    if OPTION in ['-m', '-M', '-a', '-A']:
        plot_graph('/tmp/kamstrupd/site/img/kam_vs_month_p.png',
                   fetch_last_months(),
                   "Verbruik per maand afgelopen jaren"
                  )


if __name__ == "__main__":
    main()
