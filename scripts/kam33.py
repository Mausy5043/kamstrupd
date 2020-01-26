#!/usr/bin/env python3

"""Create trendbargraphs for various periods of solar radiation."""

import os
import sqlite3 as s3
import sys
from datetime import datetime as dt

import matplotlib.pyplot as plt

DATABASE = os.environ['HOME'] + "/.sqlite3/weerdata.sqlite3"


def get_cli_params(expected_amount):
  """Check for presence of a CLI parameter."""
  if len(sys.argv) != (expected_amount + 1):
    print(f"{expected_amount} arguments expected, {len(sys.argv) - 1} received.")
    sys.exit(0)
  return sys.argv[1]


def get_historic_data(grouping, period, timeframe, from_start_of_year=False):
  """
    Fetch data
    """
  ret_T_data = []
  ret_S_data = []
  ret_lbls = []
  if from_start_of_year:
    interval = f"datetime(datetime(\'now\', \'-{period} {timeframe}\'), \'start of year\')"
  else:
    interval = f"datetime(\'now\', \'-{period} {timeframe}\')"
  db_con = s3.connect(DATABASE)
  with db_con:
    db_cur = db_con.cursor()
    db_cur.execute(f"SELECT strftime('{grouping}',sample_time) as grouped, \
                     AVG(temperature), \
                     AVG(solrad), \
                     MIN(sample_epoch) as t \
                     FROM weather \
                     WHERE (sample_time >= {interval}) \
                     GROUP BY grouped \
                     ORDER BY t ASC \
                     ;"
                   )
    db_data = db_cur.fetchall()

  for row in db_data:
    ret_T_data.append(row[1])
    ret_S_data.append(row[2] / 1000 * 3600)  # convert solar radiation in 10' avg W/m2   to   kWh/m2
    ret_lbls.append(row[0])

  return ret_T_data[-period:], ret_S_data[-period:], ret_lbls[-period:]


def fetch_last_day():
  """
    ...
    """
  trend_T_data, trend_S_data, data_lbls = get_historic_data('%d %Hh', 50, 'hour')
  return data_lbls, trend_T_data, trend_S_data


def fetch_last_month():
  """
    ...
    """
  trend_T_data, trend_S_data, data_lbls = get_historic_data('%m-%d', 33, 'day')
  return data_lbls, trend_T_data, trend_S_data


def fetch_last_year():
  """
    ...
    """
  trend_T_data, trend_S_data, data_lbls = get_historic_data('%Y-%m', 61, 'month')
  return data_lbls, trend_T_data, trend_S_data


def fetch_last_years():
  """
    ...
    """
  trend_T_data, trend_S_data, data_lbls = get_historic_data('%Y', 6, 'year', from_start_of_year=True)
  return data_lbls, trend_T_data, trend_S_data


def plot_graph(output_file, data_tuple, plot_title):
  """
    ...
    """
  data_lbls = data_tuple[0]
  trend_T_data = data_tuple[1]
  trend_S_data = data_tuple[2]

  # Set the bar width
  bar_width = 0.75
  # Set the color alpha
  ahpla = 0.7
  # positions of the left bar-boundaries
  tick_pos = list(range(1, len(data_lbls) + 1))

  # Create the general plot and the bar
  plt.rc('font', size=13)
  dummy, ax1 = plt.subplots(1, figsize=(20, 7))

  # Create a bar plot of usage_slf
  ax1.bar(tick_pos, trend_S_data,
          width=bar_width,
          label='Zonnekracht',
          alpha=ahpla,
          color='r',
          align='center'
          )
  ax1.line(tick_pos, trend_T_data,
           label='Temperatuur',
           color='k',
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
               f"Trend per uur ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
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
