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
  time mysql -h sql --skip-column-names -e     \
  "USE domotica;                          \
  SELECT *                                \
  FROM kamstrup                           \
  WHERE (sample_time >=NOW() - $interval) \
  ;"                                      \
  | sed 's/\t/;/g;s/\n//g'                \
  | awk 'NR % 10080 == 0' > "$datastore/kamyr.csv"

  #http://www.sitepoint.com/understanding-sql-joins-mysql-database/
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT ds18.sample_time, ds18.sample_epoch, ds18.temperature, wind.speed FROM ds18 INNER JOIN wind ON ds18.sample_epoch = wind.sample_epoch WHERE (ds18.sample_time) >=NOW() - INTERVAL 1 MINUTE;" | sed 's/\t/;/g;s/\n//g' > $datastore/sql2c.csv
popd >/dev/null
