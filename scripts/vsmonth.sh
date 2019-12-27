#!/bin/bash

# query monthly totals for a period of n years


interval="-5 year"

pushd "${HOME}/kamstrupd" >/dev/null || exit 1
  #shellcheck disable=SC1091
  source ./scripts/environment.sh
  # totals per hour for T1in, T2in, T1out, T2out

  #shellcheck disable=SC2154
  sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
     ".separator '; '" \
     "SELECT strftime('%Y-%m',sample_time) as annomoon, \
             (MAX(T1in)-MIN(T1in) + MAX(T2in)-MIN(T2in))/1000, \
             (MAX(T1out)-MIN(T1out) + MAX(T2out)-MIN(T2out))/1000 \
      FROM kamstrup \
      WHERE (sample_time >= datetime(datetime('now', '${interval}'), 'start of year') ) \
      GROUP BY annomoon \
      ORDER BY annomoon ASC \
      ;" > "${kamdata}"

  # convert the data into month-rows and year-columns
  # output two separate files for USAGE and PRODUCTION
  ./scripts/kam41.py "${kamdata}" || exit 1

  if [ "$(wc -l < "${kamdata}")" -gt 5 ]; then
    timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}u'" ./graphs/vsmonth_u.gp || exit 1
    timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}p'" ./graphs/vsmonth_p.gp || exit 1
  fi

  ./scripts/kam44.py -m
  ./scripts/upload.sh --upload

popd >/dev/null || exit

# drop datafiles
rm "${kamdata}"
rm "${kamdata}u"
rm "${kamdata}p"
