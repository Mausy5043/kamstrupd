#!/bin/bash

# query monthly totals for a period of n years


# interval="-61 month"

pushd "${HOME}/kamstrupd" >/dev/null || exit 1
  #shellcheck disable=SC1091
  # source ./scripts/environment.sh
  # totals per hour for T1in, T2in, T1out, T2out

  # #shellcheck disable=SC2154
  # sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
  #    ".separator '; '" \
  #    "SELECT strftime('%Y-%m',sample_time) as annomoon, \
  #            (MAX(T1in)-MIN(T1in))/1000, \
  #            (MAX(T2in)-MIN(T2in))/1000, \
  #            (MAX(T1out)-MIN(T1out))/1000, \
  #            (MAX(T2out)-MIN(T2out))/1000, \
  #            strftime('%Y',sample_time), \
  #            strftime('%m',sample_time) \
  #     FROM kamstrup \
  #     WHERE (sample_time >= datetime('now', '${interval}')) \
  #     GROUP BY annomoon \
  #     ORDER BY annomoon ASC \
  #     ;" > "${kamdata}"


  # if [ "$(wc -l < "${kamdata}")" -gt 5 ]; then
  #   timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}'" ./graphs/pastyear.gp
  # fi

  ./scripts/kam43.py -y
  ./scripts/kam44.py -m
  ./scripts/upload.sh --upload

  # # drop datafile
  # rm "${kamdata}"

  ./scripts/avgday.sh

popd >/dev/null || exit
