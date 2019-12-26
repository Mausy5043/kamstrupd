#!/usr/bin/env python3

"""."""


import os
import sqlite3 as s3

import matplotlib.pyplot as plt

DATABASE = os.environ['HOME'] + "/.sqlite3/electriciteit.sqlite3"

def get_import_lo(period):
    """
    Fetch import data LO
    """
    interval = '-{period+2} hour'
    db = sqlite3.connect(DATABASE)
    with db:
        cur = db.cursor()
        cur.execute("SELECT strftime('%d %Hh',sample_time) as grouped, \
                     MAX(T2in)-MIN(T2in), \
                     MIN(sample_epoch) as t \
                     FROM kamstrup \
                     WHERE (sample_time >= datetime('now', '${interval}')) \
                     GROUP BY grouped \
                     ORDER BY t ASC \
                     ;"
                    )
        rows = cur.fetchall()

    for row in rows:
        print row

    ret_data = [ 4, 4, 6, 4, 3, 5]
    return ret_data


def get_import_hi(interval):
    """
    Fetch import data HI
    """
    ret_data = [16, 23, 15, 10, 10, 12]
    return ret_data


def get_export_lo(interval):
    """
    Fetch export data LO
    """
    ret_data = [40, 41, 63, 35, 42, 42]
    return ret_data


def get_export_hi(interval):
    """
    Fetch export data HI
    """
    ret_data = [10,  8,  9, 12, 15, 16]
    return ret_data


def get_opwekking(interval):
    """
    Fetch production data
    """
    ret_data = [80+40+10, 82+41+8, 63+63+9, 95+35+12, 88+42+15, 86+42+16]
    return ret_data


def main():
    """
    This is the main loop
    """
    import_lo = get_import_lo(48)
    import_hi = get_import_hi(48)
    export_lo = get_export_lo(48)
    export_hi = get_export_hi(48)
    opwekking = get_opwekking(48)

    # print(import_lo)
    # print(import_hi)
    # print(opwekking)
    # print(export_hi)
    # print(export_lo)

    yr = [2012,2013,2014,2015,2016,2017]

    own_usage = [x-y-z for x,y,z in zip(opwekking, export_hi, export_lo)]
    # print(own_usage)

    #Create the general plot and the "subplots" i.e. the bars
    f, ax1 = plt.subplots(1, figsize=(20, 5))
    # Set the bar width
    bar_width = 0.75
    # Set the color alpha
    ahpla = 0.5

    # positions of the left bar-boundaries
    tick_pos = list(range(1, len(import_lo)+1))

    # Create a bar plot of import_lo
    ax1.bar(tick_pos, import_lo,
            width=bar_width,
            label='Import (L)',
            alpha=ahpla,
            color='r',
            align='center',
            bottom=[sum(i) for i in zip(import_hi, own_usage)]
            )
    # Create a bar plot of import_hi
    ax1.bar(tick_pos, import_hi,
            width=bar_width,
            label='Import (H)',
            alpha=ahpla,
            color='y',
            align='center',
            bottom=own_usage
            )
    # Create a bar plot of usage_slf
    ax1.bar(tick_pos, own_usage,
            width=bar_width,
            label='Self',
            alpha=ahpla,
            color='g',
            align='center'
            )
    # Create a bar plot of export_lo
    ax1.bar(tick_pos, [-1*i for i in export_lo],
            width=bar_width,
            label='Export (L)',
            alpha=ahpla,
            color='c',
            align='center'
            )
    # Create a bar plot of export_hi
    ax1.bar(tick_pos, [-1*i for i in export_hi],
            width=bar_width,
            label='Export (H)',
            alpha=ahpla,
            color='b',
            align='center',
            bottom=[-1*i for i in export_lo]
            )

    # set the x ticks with names
    plt.xticks(tick_pos, yr)

    # Set the label and legends
    ax1.set_ylabel("[kWh]")
    ax1.set_xlabel("Datetime")
    ax1.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
    plt.legend(loc='center left')
    ax1.axhline(y=0, color='k')
    ax1.axvline(x=0, color='k')

    # Set a buffer around the edge
    plt.xlim([min(tick_pos)-bar_width, max(tick_pos)+bar_width])
    plt.savefig(fname='graph.png', format='png')


if __name__ == "__main__":
    main()
