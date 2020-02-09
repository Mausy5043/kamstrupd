#!/usr/bin/env python3

"""."""

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

  return ret_data, ret_lbls


def get_opwekking(period, timeframe, from_start_of_year=False):
  """
    Fetch production data
    """
  ret_data = [[0] * 24]
  return ret_data


def reshape_to_hourly(data, labels):
  """
    ...
    """
  ret_data = [[] for _ in range(0, 24)]
  ret_lbls = ['00h', '01h', '02h', '03h', '04h', '05h', '06h', '07h', '08h', '09h',
              '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h', '19h',
              '20h', '21h', '22h', '23h'
              ]
  for data_idx in range(0, len(data)):
    datum_num = data[data_idx]
    datum_tim = labels[data_idx].split(' ')[2]
    datum_ptr = ret_lbls.index(datum_tim)
    ret_data[datum_ptr].append(datum_num)
  return ret_data, ret_lbls


def fetch_avg_day():
  """
    ...
    """
  import_lo, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 1, 'year', 'T1in', from_start_of_year=True))
  import_hi, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 1, 'year', 'T2in', from_start_of_year=True))
  export_lo, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 1, 'year', 'T1out', from_start_of_year=True))
  export_hi, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 1, 'year', 'T2out', from_start_of_year=True))
  opwekking = get_opwekking(1, 'year', from_start_of_year=True)
  return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def contract(array1, array2):
  result = []
  for idx_hr in range(0, len(array1)):
    result.append([x + y for x, y in zip(array1[idx_hr], array2[idx_hr])])
  return result


def plot_graph(output_file, data_tuple, plot_title):
  """
    ...
    """
  data_lbls = data_tuple[0]
  import_lo = data_tuple[1]
  import_hi = data_tuple[2]
  imprt = contract(import_lo, import_hi)
  # opwekking = data_tuple[3]
  # export_lo = data_tuple[4]
  # export_hi = data_tuple[5]
  # exprt = [x1 + x2 for x1, x2 in zip(export_lo, export_hi)]
  # own_usage = [x - y - z for x, y, z in zip(opwekking, export_hi, export_lo)]

  # Set the bar width
  bar_width = 0.75
  # Set the color alpha
  ahpla = 0.7
  # positions of the left bar-boundaries
  tick_pos = list(range(1, len(data_lbls) + 1))

  # Create the general plot and the bar
  plt.rc('font', size=13)
  dummy, ax1 = plt.subplots(1, figsize=(20, 7))

  # for x_data in imprt:
  ax1.boxplot(imprt,
              notch=True,
              showbox=True,
              showcaps=True,
              showfliers=False,
              showmeans=True,
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
    plot_graph('/tmp/kamstrupd/site/img/kam_avg_day_p.png',
               fetch_avg_day(),
               f"Typisch uurverbruik ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})"
               )




if __name__ == "__main__":
  main()
