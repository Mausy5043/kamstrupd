#!/bin/bash

# query hourly totals for a period of two days (48 hours)


interval="-48 hour"

pushd "${HOME}/kamstrupd" >/dev/null || exit 1
  #shellcheck disable=SC1091
  # source ./scripts/environment.sh
  # totals per hour for T1in, T2in, T1out, T2out

  # #shellcheck disable=SC2154
  # sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
  #    ".separator '; '" \
  #    "SELECT strftime('%d %Hh',sample_time) as solhour, \
  #            MAX(T1in)-MIN(T1in), \
  #            MAX(T2in)-MIN(T2in), \
  #            MAX(T1out)-MIN(T1out), \
  #            MAX(T2out)-MIN(T2out), \
  #            MIN(sample_epoch) as t \
  #     FROM kamstrup \
  #     WHERE (sample_time >= datetime('now', '${interval}')) \
  #     GROUP BY solhour \
  #     ORDER BY t ASC \
  #     ;" > "${kamdata}"

  # if [ "$(wc -l < "${kamdata}")" -gt 5 ]; then
  #   timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}'" ./graphs/pastday.gp
  # fi

  ./scripts/kam43.py -d
  ./scripts/upload.sh --upload

  # # drop datafile
  # rm "${kamdata}"

popd >/dev/null || exit
