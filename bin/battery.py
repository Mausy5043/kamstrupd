#!/usr/bin/env python3

"""Retrieve data for battery sizing investigations.
18AUG2021
$ python3 battery.py -d 360 -m 5.4 -s 5
Passed options: Namespace(days=360, hours=None, maxbat=5.4, soc=5.0)
Parsed options: Namespace(days=360, hours=8640, maxbat=5400.0, soc=5000.0)

Max. Battery SoC : 5400 Wh 	 cumul : 19121 kWh
Max. Surplus     : 2662 Wh 	 cumul : 1381 kWh
Max. Shortage    : 5397 Wh 	 cumul : 1308 kWh

"""

import argparse
import os
import sqlite3
import warnings

import numpy as np
import pandas as pd

import constants

warnings.filterwarnings('ignore')

# runlist id for daemon :
MYID = 'DEFAULT'
# app_name :
HERE = os.path.realpath(__file__).split('/')
MYAPP = HERE[-3]
MYROOT = "/".join(HERE[0:-3])
NODE = os.uname()[1]
ROOM_ID = NODE[-2:]

# DATABASE = f"{MYROOT}/{constants.BATTERY['database']}"
DATABASE = constants.BATTERY['database']
print(DATABASE)


def fetch_data(hours_to_fetch):
    """

    Args:
        hours_to_fetch (int): number of hours of data to query from the DB

    Returns:
        (pandas.DataFrame): data queried

    """
    global DATABASE
    global OPTION
    where_condition = f" (sample_time >= datetime(\'now\', \'-{hours_to_fetch + 1} hours\'))"
    sql_query = f"SELECT sample_time, strftime('%s', sample_time) as hr, MIN(sample_time) as st, " \
                f"       T1in, T1out, T2in, T2out " \
                f"FROM kamstrup " \
                f"WHERE {where_condition} " \
                f"GROUP BY strftime('%Y%m%d%H', sample_time) "
    with sqlite3.connect(DATABASE) as con:
        df = pd.read_sql_query(sql_query,
                               con,
                               parse_dates='sample_time',
                               index_col='sample_time'
                               )
    # sort by datetime
    df = df.sort_index('index')
    # drop the column used for filtering
    df = df.drop(columns=['st'])
    print(df['hr'])
    # convert the epoch seconds from str to int32 and into hours
    df['hr'] = df.astype({'hr': 'int32'}) / 3600
    # calculate the hourly values
    df = df.diff()
    # aggregate imports and exports
    df['in'] = (df['T1in'] + df['T2in']) / df['hr']
    df['out'] = (df['T1out'] + df['T2out']) / df['hr']
    # determine the hourly delta; surplus(+) or shortage(-)
    df['delta'] = df['in'] - df['out']
    # reset the index to be able to navigate through the rows
    df.reset_index(inplace=True)
    return df


def assess_battery(df):
    """

    Args:
        df (pandas.DataFrame): raw data from database

    Returns:
        (pandas.DataFrame): battery balance data added

    """
    global OPTION
    # set-up the battery with a pre-charge
    df['battery'] = OPTION.soc
    # start off the surplus at zero
    df['surplus'] = 0
    # start off the shortage at zero
    df['shortge'] = 0
    for i in range(1, len(df)):
        # determine battery SoC at the top of the hour
        bat_state = df.loc[i - 1, 'battery']
        # add the hour's surplus to the battery
        surplus = df.loc[i, 'out']
        bat_state += surplus
        surplus = 0
        # skim off the surplus that doesn't fit in the battery if it tops out
        if bat_state > OPTION.maxbat:
            surplus = bat_state - OPTION.maxbat
            bat_state = OPTION.maxbat
        # remove the hour's shortage from the battery
        shortge = df.loc[i, 'in']
        bat_state -= shortge
        shortge = 0
        # determine the energy to import if the battery is drained
        if bat_state < 0:
            shortge = 0 - bat_state
            bat_state = 0
        # store the balance
        df.loc[i, 'battery'] = bat_state
        df.loc[i, 'surplus'] = surplus
        df.loc[i, 'shortge'] = shortge

    df.reset_index(drop=True, inplace=True)
    return df


def main():
    """
      This is the main loop
      """
    global MYAPP
    global OPTION
    data = None
    if OPTION.hours:
        data = assess_battery(fetch_data(OPTION.hours))
    if OPTION.days:
        data = assess_battery(fetch_data(OPTION.days * 24))

    # pd.set_option("display.max_rows", None, "display.max_columns", None)
    # print(data)
    print(f"Max. Battery SoC : {np.max(data['battery']):.0f} Wh \t cumul : {np.sum(data['battery']) / 1000:.0f} kWh")
    print(f"Max. Surplus     : {np.max(data['surplus']):.0f} Wh \t cumul : {np.sum(data['surplus']) / 1000:.0f} kWh")
    print(f"Max. Shortage    : {np.max(data['shortge']):.0f} Wh \t cumul : {np.sum(data['shortge']) / 1000:.0f} kWh")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch data")
    parser.add_argument('-hr',
                        '--hours',
                        type=int,
                        help='fetch hourly-data for <HOURS> hours '
                        )
    parser.add_argument('-d',
                        '--days',
                        type=int,
                        help='fetch hourly-data for <DAYS> days'
                        )
    parser.add_argument('-m',
                        '--maxbat',
                        default=5.0,
                        type=float,
                        help='maximum battery capacity [kWh]'
                        )
    parser.add_argument('-s',
                        '--soc',
                        type=float,
                        help='battery SoC [kWh]'
                        )
    OPTION = parser.parse_args()
    print(f"Passed options: {OPTION}")
    if not OPTION.hours or OPTION.hours == 0:
        OPTION.hours = 50
    if OPTION.days and OPTION.days > 0:
        OPTION.hours = OPTION.days * 24
    if OPTION.soc is None:
        OPTION.soc = OPTION.maxbat
    # scale to Wh
    OPTION.soc *= 1000
    OPTION.maxbat *= 1000

    print(f"Parsed options: {OPTION}")
    print("")
    main()
