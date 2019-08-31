#!/bin/bash

# query hourly totals for a period of two days (48 hours)

# create a place to store the data
datastore="/tmp/kamstrupd/data"
if [ ! -d "$datastore" ]; then
  mkdir -p "$datastore"
fi

interval="-48 hour"
divisor="3600"

pushd "$HOME/kamstrupd" >/dev/null || exit 1
  # totals per hour for T1in, T2in, T1out, T2out
  sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
     ".separator '. '" \
     "SELECT strftime('%H',sample_time), \
             MAX(T1in)-MIN(T1in), \
             MAX(T2in)-MIN(T2in), \
             MAX(T1out)-MIN(T1out), \
             MAX(T2out)-MIN(T2out) \
      FROM kamstrup \
      WHERE (sample_time >= datetime('now', '${interval}')) \
      GROUP BY ((sample_epoch - (sample_epoch % ${divisor})) / ${divisor}) \
      ;"

popd >/dev/null || exit
