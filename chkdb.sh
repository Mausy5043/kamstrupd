#!/bin/sh

arg1="$1"

echo "--Looking for entries with zero value counter--"
mysql -h sql -e "USE domotica; SELECT * FROM kamstrup WHERE (T1in = 0 OR T2in = 0);"
echo

if [[ "$arg1" == "-d" ]]; then
  echo "Deleting data in 5s"
  sleep 5 && mysql -h sql -e "USE domotica; DELETE FROM kamstrup WHERE (T1in = 0 OR T2in = 0);"
fi
