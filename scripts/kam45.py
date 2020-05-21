#!/usr/bin/env python3

"""."""

import os
import warnings
from datetime import datetime as dt

# noinspection PyUnresolvedReferences
import kamlib as kl
import matplotlib.pyplot as plt
import numpy as np

DATABASE = os.environ['HOME'] + "/.sqlite3/electriciteit.sqlite3"


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
    datum_val = data[data_idx]
    datum_tim = labels[data_idx].split(' ')[2]
    datum_ptr = ret_lbls.index(datum_tim)
    ret_data[datum_ptr].append(datum_val)
  return np.array(ret_data), np.array(ret_lbls)


def fetch_avg_day():
  """
    ...
    """
  config = kl.add_time_line({'grouping': '%Y %j %Hh',
                             'period': 24 * 366 * 2,
                             'timeframe': 'hour',
                             'database': DATABASE,
                             'table': 'production'
                             })
  opwekking, prod_lbls = reshape_to_hourly(
    *kl.get_historic_data(config, telwerk='energy', from_start_of_year=True, include_today=False))
  config['table'] = 'kamstrup'
  import_lo, data_lbls = reshape_to_hourly(
    *kl.get_historic_data(config, telwerk='T1in', from_start_of_year=True, include_today=False))
  import_hi, data_lbls = reshape_to_hourly(
    *kl.get_historic_data(config, telwerk='T2in', from_start_of_year=True, include_today=False))
  export_lo, data_lbls = reshape_to_hourly(
    *kl.get_historic_data(config, telwerk='T1out', from_start_of_year=True, include_today=False))
  export_hi, data_lbls = reshape_to_hourly(
    *kl.get_historic_data(config, telwerk='T2out', from_start_of_year=True, include_today=False))
  return data_lbls, import_lo, import_hi, opwekking, export_lo, export_hi


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
  imprt = kl.contract24(import_lo, import_hi)
  exprt = kl.contract24(export_lo, export_hi)
  own_usage = kl.distract24(opwekking, exprt)
  usage = kl.contract24(own_usage, imprt)
  """
  --- Start debugging:
  np.set_printoptions(precision=3)
  hr = 13
  print("data_lbls: ", np.size(data_lbls), data_lbls[hr][-5:])
  print(" ")
  print("opwekking: ", np.size(opwekking), opwekking[hr][-5:])
  print(" ")
  print("export_hi: ", np.size(export_hi), export_hi[hr][-5:])
  print("export_lo: ", np.size(export_lo), export_lo[hr][-5:])
  print("exprt    : ", np.size(exprt), exprt[hr][-5:])
  print(" ")
  print("import_hi: ", np.size(import_hi), import_hi[hr][-5:])
  print("import_lo: ", np.size(import_lo), import_lo[hr][-5:])
  print("imprt    : ", np.size(imprt), imprt[hr][-5:])
  print(" ")
  print("own_usage: ", np.size(own_usage), own_usage[hr][-5:])
  print("usage    : ", np.size(usage), usage[hr][-5:])
  print(" ")
  --- End debugging.
  """
  if imorex == "u":
    x_data = usage
  if imorex == "p":
    x_data = opwekking
  if imorex == "s":
    x_data = []
    for row in exprt:
      ax = np.array(row)
      with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        ax[ax == 0] = np.nan
        x_data.append(np.nanmedian(ax))
    x_data = np.array(x_data)

  # Set the bar width
  bar_width = 0.75
  # Set the color alpha
  ahpla = 0.4
  # positions of the left bar-boundaries
  tick_pos = list(range(1, len(data_lbls) + 1))

  # Create the general plot and the bar
  plt.rc('font', size=13)
  dummy, ax1 = plt.subplots(1, figsize=(20, 7))

  if imorex == "s":
    ax1.bar(tick_pos, x_data,
            width=bar_width,
            alpha=ahpla,
            color='b',
            align='center',
            )
  else:
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
  OPTION = kl.get_cli_params(1)
  avg_day = fetch_avg_day()
  if OPTION in ['-u', '-U', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_avg_day_u.png',
               avg_day,
               f"Typisch stroomgebruik per uur ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
               imorex="u"
               )

  if OPTION in ['-p', '-P', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_avg_day_p.png',
               avg_day,
               f"Typische opwekking per uur ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
               imorex="p"
               )

  if OPTION in ['-s', '-S', '-a', '-A']:
    plot_graph('/tmp/kamstrupd/site/img/kam_avg_day_s.png',
               avg_day,
               f"Typisch overschot per uur ({dt.now().strftime('%d-%m-%Y %H:%M:%S')})",
               imorex="s"
               )


if __name__ == "__main__":
  main()
