#!/bin/bash

# Pull data from MySQL server and graph them.

datastore="/tmp/kamstrupd/mysql"

if [ ! -d "$datastore" ]; then
  mkdir -p "$datastore"
fi

# host=$(hostname)

pushd "$HOME/kamstrupd" >/dev/null
  #week (per hour = 60')
  interval="INTERVAL 8 DAY "
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM kamstrup where (sample_time >=NOW() - $interval);" | sed 's/\t/;/g;s/\n//g' |\
  awk 'NR % 60 == 0' > "$datastore/kamwr.csv"

  #month (per day =  1440')
  interval="INTERVAL 32 DAY "
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM kamstrup where (sample_time >=NOW() - $interval);" | sed 's/\t/;/g;s/\n//g' |\
  awk 'NR % 1440 == 0' > "$datastore/kammr.csv"

  #year (per week = 10080')
  interval="INTERVAL 370 DAY "
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM kamstrup where (sample_time >=NOW() - $interval);" | sed 's/\t/;/g;s/\n//g' |\
  awk 'NR % 10800 == 0' > "$datastore/kamyr.csv"

  #http://www.sitepoint.com/understanding-sql-joins-mysql-database/
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT ds18.sample_time, ds18.sample_epoch, ds18.temperature, wind.speed FROM ds18 INNER JOIN wind ON ds18.sample_epoch = wind.sample_epoch WHERE (ds18.sample_time) >=NOW() - INTERVAL 1 MINUTE;" | sed 's/\t/;/g;s/\n//g' > $datastore/sql2c.csv
popd >/dev/null
