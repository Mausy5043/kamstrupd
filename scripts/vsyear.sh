#!/bin/bash

# query yearly totals for a period of n years


interval="-5 year"

pushd "${HOME}/kamstrupd" >/dev/null || exit 1
  #shellcheck disable=SC1091
  source ./scripts/environment.sh
  # totals per hour for T1in, T2in, T1out, T2out

  #shellcheck disable=SC2154
  sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
     ".separator '; '" \
     "SELECT strftime('%Y',sample_time) as anno, \
             (MAX(T1in)-MIN(T1in))/1000, \
             (MAX(T2in)-MIN(T2in))/1000, \
             (MAX(T1out)-MIN(T1out))/1000, \
             (MAX(T2out)-MIN(T2out))/1000 \
      FROM kamstrup \
      WHERE (sample_time >= datetime('now', '${interval}')) \
      GROUP BY anno \
      ORDER BY anno ASC \
      ;" > "${kamdata}"

  if [ "$(wc -l < "${kamdata}")" -gt 5 ]; then
    timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}'" ./graphs/vsyear.gp
  fi

  ./scripts/upload.sh --upload

  # drop datafile
  rm "${kamdata}"

popd >/dev/null || exit
