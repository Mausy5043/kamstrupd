#!/bin/bash

# Pull data from MySQL server.

datastore="/tmp/kamstrupd/mysql"

if [ ! -d "$datastore" ]; then
  mkdir -p "$datastore"
fi

# host=$(hostname)

pushd "$HOME/kamstrupd" >/dev/null
  #week (per hour = 60')
  interval="INTERVAL 8 DAY "
  # time mysql -h sql --skip-column-names -e     \
  # "USE domotica;                          \
  # SELECT *                                \
  # FROM kamstrup                           \
  # WHERE (sample_time >=NOW() - $interval) \
  # ;"                                      \
  # | sed 's/\t/;/g;s/\n//g'                \
  # | awk 'NR % 60 == 0' > "$datastore/kamwr.csv"

  time mysql --defaults-file=.my.kam.cnf -h sql --skip-column-names -e       \
  "USE domotica;                             \
   SELECT MIN(sample_epoch),                 \
          MAX(T1in),                         \
          MAX(T2in),                         \
          AVG(powerin)                       \
    FROM kamstrup                            \
    WHERE (sample_time >=NOW() - $interval)  \
    GROUP BY (sample_epoch DIV 3600)         \
   ;"                                        \
  | sed 's/\t/;/g;s/\n//g' > "$datastore/kamw2.csv"

  #month (per day =  1440')
  # 24h*60m = 1440m
  interval="INTERVAL 32 DAY "
  # time mysql -h sql --skip-column-names -e     \
  # "USE domotica;                          \
  # SELECT *                                \
  # FROM kamstrup                           \
  # WHERE (sample_time >=NOW() - $interval) \
  # ;"                                      \
  # | sed 's/\t/;/g;s/\n//g'                \
  # | awk 'NR % 1440 == 0' > "$datastore/kammr.csv"

  time mysql --defaults-file=.my.kam.cnf -h sql --skip-column-names -e       \
  "USE domotica;                             \
   SELECT MIN(sample_epoch),                 \
          MAX(T1in),                         \
          MAX(T2in),                         \
          AVG(powerin)                       \
    FROM kamstrup                            \
    WHERE (sample_time >=NOW() - $interval)  \
    GROUP BY YEAR(sample_time),              \
             MONTH(sample_time),             \
             DAY(sample_time)                \
   ;"                                        \
  | sed 's/\t/;/g;s/\n//g' > "$datastore/kamm2.csv"

  #http://www.sitepoint.com/understanding-sql-joins-mysql-database/
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT ds18.sample_time, ds18.sample_epoch, ds18.temperature, wind.speed FROM ds18 INNER JOIN wind ON ds18.sample_epoch = wind.sample_epoch WHERE (ds18.sample_time) >=NOW() - INTERVAL 1 MINUTE;" | sed 's/\t/;/g;s/\n//g' > $datastore/sql2c.csv
popd >/dev/null
