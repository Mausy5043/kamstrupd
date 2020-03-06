#!/usr/bin/env python3

"""Common functions for use by kam*.py scripts"""

import sqlite3 as s3
import sys

import numpy as np


def build_arrays44(lbls, use_data, expo_data):
  """Use the input to build two arrays and return them.

     example input line : "2015-01; 329811; 0"  : YYYY-MM; T1; T2
     the list comes ordered by the first field
     the first line and last line can be inspected to find
     the first and last year in the dataset.
    """
  first_year = int(lbls[0].split('-')[0])
  last_year = int(lbls[-1].split('-')[0]) + 1
  num_years = last_year - first_year

  label_lists = [np.arange(first_year, last_year), np.arange(1, 13)]
  usage = np.zeros((num_years, 12))
  exprt = np.zeros((num_years, 12))

  for data_point in zip(lbls, use_data, expo_data):
    [year, month] = data_point[0].split('-')
    col_idx = int(month) - 1
    row_idx = int(year) - first_year
    usage[row_idx][col_idx] = data_point[1]
    exprt[row_idx][col_idx] = data_point[2]
  return label_lists, usage, exprt


def contract(arr1, arr2):
  """
  Add two arrays together.
  """
  size = max(len(arr1), len(arr2))
  rev_arr1 = np.zeros(size, dtype=float)
  rev_arr2 = np.zeros(size, dtype=float)
  for idx in range(0, len(arr1)):
    rev_arr1[idx] = arr1[::-1][idx]
  for idx in range(0, len(arr2)):
    rev_arr2[idx] = arr2[::-1][idx]
  result = np.sum([rev_arr1, rev_arr2], axis=0)
  return result[::-1]


def contract24(arr1, arr2):
  result = [[]] * 24
  for hr in range(0, 24):
    result[hr] = contract(arr1[hr], arr2[hr])

  return result


def distract(arr1, arr2):
  """
  Subtract two arrays.
  Note: order is important!
  """
  size = max(len(arr1), len(arr2))
  rev_arr1 = np.zeros(size, dtype=float)
  rev_arr2 = np.zeros(size, dtype=float)
  for idx in range(0, len(arr1)):
    rev_arr1[idx] = arr1[::-1][idx]
  for idx in range(0, len(arr2)):
    rev_arr2[idx] = arr2[::-1][idx]
  result = np.subtract(rev_arr1, rev_arr2)
  result[result < 0] = 0.0
  return result[::-1]


def distract24(arr1, arr2):
  result = [[]] * 24
  for hr in range(0, 24):
    result[hr] = distract(arr1[hr], arr2[hr])
  return result


def get_cli_params(expected_amount):
  """Check for presence of a CLI parameter."""
  if len(sys.argv) != (expected_amount + 1):
    print(f"{expected_amount} arguments expected, {len(sys.argv) - 1} received.")
    sys.exit(0)
  return sys.argv[1]


def get_historic_data(dicti, telwerk=None, from_start_of_year=False, include_today=True):
  """Fetch historic data from SQLITE3 database.

  :param
  dict: dict - containing settings
  telwerk: str - columnname to be collected
  from_start_of_year: boolean - fetch data from start of year or not

  :returns
  ret_data: numpy list int - data returned
  ret_lbls: numpy list str - label texts returned
  """
  period = dicti['period']
  if from_start_of_year:
    interval = f"datetime(datetime(\'now\', \'-{period} {dicti['timeframe']}\'), \'start of year\')"
  else:
    interval = f"datetime(\'now\', \'-{period} {dicti['timeframe']}\')"
  if include_today:
    and_where_not_today = ''
  else:
    and_where_not_today = 'AND (sample_time <= datetime(\'now\', \'-1 day\'))'
  db_con = s3.connect(dicti['database'])
  with db_con:
    db_cur = db_con.cursor()
    db_cur.execute(f"SELECT strftime('{dicti['grouping']}',sample_time) as grouped, \
                     MAX({telwerk})-MIN({telwerk}), \
                     MIN(sample_epoch) as t \
                     FROM {dicti['table']} \
                     WHERE (sample_time >= {interval}) \
                        {and_where_not_today} \
                     GROUP BY grouped \
                     ORDER BY t ASC \
                     ;"
                   )
    db_data = db_cur.fetchall()

  data = np.array(db_data)
  ret_data = np.array(data[:, 1], dtype=float) / 1000
  ret_lbls = np.array(data[:, 0], dtype=str)

  return ret_data[-period:], ret_lbls[-period:]
