#!/usr/bin/env python3

"""Create trendbargraphs for various periods of electricity use and production."""

import os
import sqlite3 as s3
import sys
from datetime import datetime as dt

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
    ret_data.append(row[1] / 1000)  # convert Wh to kWh
    ret_lbls.append(row[0])

  return ret_data[-period:], ret_lbls[-period:]


def get_opwekking(period, timeframe, from_start_of_year=False):
  """
    Fetch production data
    """
  ret_data = [0] * period
  return ret_data


def fetch_last_day():
  """
    ...
    """
  import_lo, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T1in')
  import_hi, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T2in')
  export_lo, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T1out')
  export_hi, data_lbls = get_historic_data('%d %Hh', 50, 'hour', 'T2out')
  opwekking = get_opwekking(50, 'hour')
  return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def fetch_last_month():
  """
    ...
    """
  import_lo, data_lbls = get_historic_data('%m-%d', 33, 'day', 'T1in')
  import_hi, data_lbls = get_historic_data('%m-%d', 33, 'day', 'T2in')
  export_lo, data_lbls = get_historic_data('%m-%d', 33, 'day', 'T1out')
  export_hi, data_lbls = get_historic_data('%m-%d', 33, 'day', 'T2out')
  opwekking = get_opwekking(33, 'day')
  return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def fetch_last_year():
  """
    ...
    """
  import_lo, data_lbls = get_historic_data('%Y-%m', 61, 'month', 'T1in')
  import_hi, data_lbls = get_historic_data('%Y-%m', 61, 'month', 'T2in')
  export_lo, data_lbls = get_historic_data('%Y-%m', 61, 'month', 'T1out')
  export_hi, data_lbls = get_historic_data('%Y-%m', 61, 'month', 'T2out')
  opwekking = get_opwekking(61, 'month')
  return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def fetch_last_years():
  """
    ...
    """
  import_lo, data_lbls = get_historic_data('%Y', 6, 'year', 'T1in', from_start_of_year=True)
  import_hi, data_lbls = get_historic_data('%Y', 6, 'year', 'T2in', from_start_of_year=True)
  export_lo, data_lbls = get_historic_data('%Y', 6, 'year', 'T1out', from_start_of_year=True)
  export_hi, data_lbls = get_historic_data('%Y', 6, 'year', 'T2out', from_start_of_year=True)
  opwekking = get_opwekking(6, 'year', from_start_of_year=True)
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
  own_usage = [x - y - z for x, y, z in zip(opwekking, export_hi, export_lo)]

  # Set the bar width
  bar_width = 0.75
  # Set the color alpha
  ahpla = 0.7
  # positions of the left bar-boundaries
  tick_pos = list(range(1, len(data_lbls) + 1))

  # Create the general plot and the bar
  plt.rc('font', size=13)
  dummy, ax1 = plt.subplots(1, figsize=(20, 7))

  # Create a bar plot of import_lo
  ax1.bar(tick_pos, import_hi,
          width=bar_width,
          label='Import (T2)',
          alpha=ahpla,
          color='y',
          align='center',
          bottom=[sum(i) for i in zip(import_lo, own_usage)]
          )
  # Create a bar plot of import_hi
  ax1.bar(tick_pos, import_lo,
          width=bar_width,
          label='Import (T1)',
          alpha=ahpla,
          color='b',
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
  # Exports hang below the y-axis
  # Create a bar plot of export_lo
  ax1.bar(tick_pos, [-1 * i for i in export_lo],
          width=bar_width,
          label='Export (T1)',
          alpha=ahpla,
          color='c',
          align='center'
          )
  # Create a bar plot of export_hi
  ax1.bar(tick_pos, [-1 * i for i in export_hi],
          width=bar_width,
          label='Export (T2)',
          alpha=ahpla,
          color='r',
          align='center',
          bottom=[-1 * i for i in export_lo]
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
  plt.xlim([min(tick_pos) - bar_width, max(tick_pos) + bar_width])
  plt.tight_layout()
  plt.savefig(fname=f'{output_file}', format='png')


def main():
  """
    This is the main loop
    """
  OPTION = get_cli_params(1)

  if OPTION in ['-d', '-D', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_pastday.png',
               fetch_last_day(),
               f"Verbruiktrend per uur ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
               )

  if OPTION in ['-m', '-M', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_pastmonth.png',
               fetch_last_month(),
               f"Verbruikstrend per dag afgelopen maand ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
               )

  if OPTION in ['-y', '-Y', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_pastyear.png',
               fetch_last_year(),
               f"Verbruikstrend per maand afgelopen jaren ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
               )
    plot_graph('/tmp/kamstrupd/site/img/kam_vs_year.png',
               fetch_last_years(),
               f"Verbruikstrend per jaar afgelopen jaren ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
               )


if __name__ == "__main__":
  main()
