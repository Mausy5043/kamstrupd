#!/bin/bash

# query daily totals for a period of one month (744 hours)


interval="-1 month"

pushd "${HOME}/kamstrupd" >/dev/null || exit 1
  #shellcheck disable=SC1091
  source ./scripts/environment.sh
  # totals per hour for T1in, T2in, T1out, T2out

  # #shellcheck disable=SC2154
  # sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
  #    ".separator '; '" \
  #    "SELECT strftime('%m-%d',sample_time) as sol, \
  #            (MAX(T1in)-MIN(T1in))/1000, \
  #            (MAX(T2in)-MIN(T2in))/1000, \
  #            (MAX(T1out)-MIN(T1out))/1000, \
  #            (MAX(T2out)-MIN(T2out))/1000, \
  #            MIN(sample_epoch) as t \
  #     FROM kamstrup \
  #     WHERE (sample_time >= datetime('now', '${interval}')) \
  #     GROUP BY sol \
  #     ORDER BY t ASC \
  #     ;" > "${kamdata}"

  # if [ "$(wc -l < "${kamdata}")" -gt 5 ]; then
  #   timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}'" ./graphs/pastmonth.gp
  # fi

  ./scripts/kam43.py -m
  ./scripts/upload.sh --upload

  # drop datafile
  # rm "${kamdata}"

popd >/dev/null || exit
