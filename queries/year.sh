#!/bin/bash

# Pull data from MySQL server.

datastore="/tmp/kamstrupd/mysql"

if [ ! -d "$datastore" ]; then
  mkdir -p "$datastore"
fi

# host=$(hostname)

pushd "$HOME/kamstrupd" >/dev/null || exit 1
  #year (per week = 10080')
  # 7d*24h*60m = 10080m
  interval="INTERVAL 740 DAY "
  # time mysql -h boson --skip-column-names -e     \
  # "USE domotica;                          \
  # SELECT *                                \
  # FROM kamstrup                           \
  # WHERE (sample_time >=NOW() - $interval) \
  # ;"                                      \
  # | sed 's/\t/;/g;s/\n//g'                \
  # | awk 'NR % 10080 == 0' > "$datastore/kamyr.csv"

  time mysql --defaults-file="~/.my.kam.cnf" -h boson --skip-column-names -e       \
  "USE domotica;                             \
   SELECT MIN(sample_epoch),                 \
          MAX(T1in),                         \
          MAX(T2in),                         \
          AVG(powerin)                       \
    FROM kamstrup                            \
    WHERE (sample_time >=NOW() - $interval)  \
    GROUP BY YEAR(sample_time),              \
             MONTH(sample_time)              \
    ORDER BY sample_epoch                    \
   ;"                                        \
  | sed 's/\t/;/g;s/\n//g' | sort -t ";" -k 1 > "$datastore/kamy2.csv"

popd >/dev/null || exit
