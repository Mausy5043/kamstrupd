#!/bin/bash

# Pull data from MySQL server.

datastore="/tmp/kamstrupd/mysql"

if [ ! -d "$datastore" ]; then
  mkdir -p "$datastore"
fi

interval="INTERVAL 30 HOUR "
# host=$(hostname)

pushd "$HOME/kamstrupd" >/dev/null
  time mysql -h sql --skip-column-names -e     \
  "USE domotica;                          \
  SELECT *                                \
  FROM kamstrup                           \
  WHERE (sample_time >=NOW() - $interval) \
  ;"                                      \
  | sed 's/\t/;/g;s/\n//g' > "$datastore/kamd.csv"

  time mysql -h sql --skip-column-names -e       \
  "USE domotica;                             \
   SELECT MIN(sample_epoch),                 \
          MAX(T1in),                         \
          MAX(T2in),                         \
          AVG(powerin)                       \
    FROM kamstrup                            \
    WHERE (sample_time >=NOW() - $interval)  \
    GROUP BY (sample_epoch DIV 1800)           \
   ;"                                        \
  | sed 's/\t/;/g;s/\n//g' > "$datastore/kamd2.csv"

  #http://www.sitepoint.com/understanding-sql-joins-mysql-database/
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT ds18.sample_time, ds18.sample_epoch, ds18.temperature, wind.speed FROM ds18 INNER JOIN wind ON ds18.sample_epoch = wind.sample_epoch WHERE (ds18.sample_time) >=NOW() - INTERVAL 1 MINUTE;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql2c.csv
popd >/dev/null
