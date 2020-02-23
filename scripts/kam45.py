#!/usr/bin/env python3

"""."""

import itertools as it
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
    Fetch historic data from KAMSTRUP meter
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


def get_opwekking(grouping, period, timeframe, from_start_of_year=False):
  """
    Fetch historic data from SOLAREDGE site
    """
  ret_data = [0] * period * 24
  ret_lbls = [] * period * 24
  if from_start_of_year:
    interval = f"datetime(datetime(\'now\', \'-{period} {timeframe}\'), \'start of year\')"
  else:
    interval = f"datetime(\'now\', \'-{period} {timeframe}\')"
  db_con = s3.connect(DATABASE)
  with db_con:
    db_cur = db_con.cursor()
    db_cur.execute(f"SELECT strftime('{grouping}',sample_time) as grouped, \
                     MAX(energy)-MIN(energy), \
                     MIN(sample_epoch) as t \
                     FROM production \
                     WHERE (sample_time >= {interval}) \
                     GROUP BY grouped \
                     ORDER BY t ASC \
                     ;"
                   )
    db_data = db_cur.fetchall()

  for row in db_data:
    ret_data.append(row[1] / 1000)  # convert Wh to kWh
    ret_lbls.append(row[0])

  ret_data = ret_data[-len(ret_lbls):]
  return ret_data[-period * 24:], ret_lbls[-period * 24:]


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
  opwekking, data_lbls = reshape_to_hourly(*get_opwekking('%Y %j %Hh', 2, 'year', from_start_of_year=True))
  import_lo, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 2, 'year', 'T1in', from_start_of_year=True))
  import_hi, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 2, 'year', 'T2in', from_start_of_year=True))
  export_lo, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 2, 'year', 'T1out', from_start_of_year=True))
  export_hi, data_lbls = reshape_to_hourly(*get_historic_data('%Y %j %Hh', 2, 'year', 'T2out', from_start_of_year=True))
  return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


def contract(arr1, arr2):
  """
  Add two arrays together.
  :param arr1:   list
  :param arr2:   list
  :return:   list
  """
  result = []
  array1 = list(reversed(arr1))
  array2 = list(reversed(arr2))
  for idx_hr in range(0, len(array1)):
    result.append([sum(filter(None, [x, y])) for x, y in it.zip_longest(array1[idx_hr], array2[idx_hr])])
  return list(reversed(result))


def distract(arr1, arr2):
  """
  Subtract two arrays.
  Note: order is important!
  :param arr1:  list
  :param arr2:  list
  :return:  list
  """
  result = []
  array1 = list(reversed(arr1))
  array2 = list(reversed(arr2))
  for idx_hr in range(0, len(array1)):
    result.append([sum(filter(None, [x, -1 * y])) for x, y in it.zip_longest(array1[idx_hr], array2[idx_hr])])
  return list(reversed(result))


def plot_graph(output_file, data_tuple, plot_title, imorex="u"):
  """
    ...
    """
  x_data = list(range(0, 24))
  data_lbls = data_tuple[0]
  import_lo = data_tuple[1]
  import_hi = data_tuple[2]
  opwekking = data_tuple[3]
  export_lo = data_tuple[4]
  export_hi = data_tuple[5]
  imprt = contract(import_lo, import_hi)
  exprt = contract(export_lo, export_hi)
  own_usage = distract(opwekking, exprt)
  usage = contract(own_usage, imprt)
  if imorex == "u":
    x_data = usage
  if imorex == "p":
    x_data = exprt

  # Set the bar width
  bar_width = 0.75
  # Set the color alpha
  ahpla = 0.4
  # positions of the left bar-boundaries
  tick_pos = list(range(1, len(data_lbls) + 1))

  # Create the general plot and the bar
  plt.rc('font', size=13)
  dummy, ax1 = plt.subplots(1, figsize=(20, 7))

  # for x_data in imprt:
  ax1.boxplot(x_data,
              patch_artist=True,
              notch=False,
              showbox=True,
              boxprops=dict(facecolor='b', alpha=ahpla),
              showcaps=True,
              showfliers=False,
              showmeans=True,
              meanprops=dict(markerfacecolor='k', marker='o'),
              medianprops=dict(color='k')
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

  if OPTION in ['-u', '-U', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_avg_day_u.png',
               fetch_avg_day(),
               f"Typisch uurverbruik ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
               imorex="u"
               )

  if OPTION in ['-p', '-P', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_avg_day_p.png',
               fetch_avg_day(),
               f"Typische uurproductie ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
               imorex="p"
               )


if __name__ == "__main__":
  main()
