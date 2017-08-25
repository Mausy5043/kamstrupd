#!/bin/bash

# Pull data from MySQL server.

datastore="/tmp/kamstrupd/mysql"

if [ ! -d "$datastore" ]; then
  mkdir -p "$datastore"
fi

# host=$(hostname)

pushd "$HOME/kamstrupd" >/dev/null
  #year (per week = 10080')
  # 7d*24h*60m = 10080m
  interval="INTERVAL 370 DAY "
  # time mysql -h sql --skip-column-names -e     \
  # "USE domotica;                          \
  # SELECT *                                \
  # FROM kamstrup                           \
  # WHERE (sample_time >=NOW() - $interval) \
  # ;"                                      \
  # | sed 's/\t/;/g;s/\n//g'                \
  # | awk 'NR % 10080 == 0' > "$datastore/kamyr.csv"

  time mysql -h sql --skip-column-names -e       \
  "USE domotica;                             \
   SELECT MIN(sample_epoch),                 \
          MAX(T1in),                         \
          MAX(T2in),                         \
          AVG(powerin)                       \
    FROM kamstrup                            \
    WHERE (sample_time >=NOW() - $interval)  \
    GROUP BY YEARWEEK(sample_time,1)         \
   ;"                                        \
  | sed 's/\t/;/g;s/\n//g' > "$datastore/kamy2.csv"

popd >/dev/null
