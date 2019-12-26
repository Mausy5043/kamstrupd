#!/usr/bin/env python3

"""."""


import os
import sqlite3 as s3

import matplotlib.pyplot as plt

DATABASE = os.environ['HOME'] + "/.sqlite3/electriciteit.sqlite3"

def get_historic_data(grouping, period, timeframe, telwerk):
    """
    Fetch import data LO
    """
    ret_data = []
    ret_lbls = []
    interval = f'-{period} {timeframe}'
    db_con = s3.connect(DATABASE)
    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(f"SELECT strftime('{grouping}',sample_time) as grouped, \
                     MAX({telwerk})-MIN({telwerk}), \
                     MIN(sample_epoch) as t \
                     FROM kamstrup \
                     WHERE (sample_time >= datetime('now', '{interval}')) \
                     GROUP BY grouped \
                     ORDER BY t ASC \
                     ;"
                    )
        db_data = db_cur.fetchall()

    for row in db_data:
        ret_data.append(row[1]/1000) # convert Wh to kWh
        ret_lbls.append(row[0])
    ret_data.pop(0)
    ret_data.pop(0)
    ret_lbls.pop(0)
    ret_lbls.pop(0)
    print(ret_data)
    return ret_data, ret_lbls


def get_opwekking(period, timeframe):
    """
    Fetch production data
    """
    ret_data = [0] * period
    return ret_data


def fetch_last_day():
    import_lo, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T2in')
    import_hi, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T1in')
    export_lo, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T2out')
    export_hi, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T1out')
    opwekking = get_opwekking(50, 'hour')
    return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def fetch_last_month():
    import_lo, data_lbls = get_historic_data('%m %d', 33, 'day', 'T2in')
    import_hi, data_lbls = get_historic_data('%m %d', 33, 'day', 'T1in')
    export_lo, data_lbls = get_historic_data('%m %d', 33, 'day', 'T2out')
    export_hi, data_lbls = get_historic_data('%m %d', 33, 'day', 'T1out')
    opwekking = get_opwekking(33, 'day')
    return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def main():
    """
    This is the main loop
    """
    data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi = fetch_last_day()

    data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi = fetch_last_month()
    #import_lo, data_lbls = get_historic_data('%d %Hh', 6, 'hour', 'T2in')
    #import_hi, data_lbls = get_historic_data('%d %Hh', 6, 'hour', 'T1in')
    #export_lo, data_lbls = get_historic_data('%d %Hh', 6, 'hour', 'T2out')
    #export_hi, data_lbls = get_historic_data('%d %Hh', 6, 'hour', 'T1out')
    #opwekking = get_opwekking(6, 'hour')

    own_usage = [x-y-z for x,y,z in zip(opwekking, export_hi, export_lo)]
    # print(own_usage)

    #Create the general plot and the "subplots" i.e. the bars
    dummy, ax1 = plt.subplots(1, figsize=(20, 5))
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
    plt.xticks(tick_pos, data_lbls)

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
