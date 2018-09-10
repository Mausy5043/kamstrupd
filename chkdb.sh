#!/bin/bash

arg1="$1"

echo "--Looking for entries with zero value counter--"
mysql --defaults-file="~/.my.kam.cnf" -h sql -e "USE domotica; SELECT * FROM kamstrup WHERE (T1in = 0 OR T2in = 0);"
echo

if [[ "$arg1" = "-d" ]]; then
  echo "Deleting data in 5s.."
  sleep 5 && mysql --defaults-file="~/.my.kam.cnf" -h sql -e "USE domotica; DELETE FROM kamstrup WHERE (T1in = 0 OR T2in = 0);"
else
  echo "To remove zero value entries from the database, use:"
  echo "chkdb.sh -d"
  echo
fi
