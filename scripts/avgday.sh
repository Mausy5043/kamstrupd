#!/bin/bash

# query hourly totals for a period of two days (48 hours)


interval="-1 year"

pushd "${HOME}/kamstrupd" >/dev/null || exit 1
  #shellcheck disable=SC1091
  source ./scripts/environment.sh
  # totals per hour for T1in, T2in, T1out, T2out

  #shellcheck disable=SC2154
  sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
     ".separator '; '" \
     "SELECT strftime('%j-%H',sample_time) as solhour, \
             (MAX(T1in)-MIN(T1in) + MAX(T2in)-MIN(T2in)), \
             (MAX(T1out)-MIN(T1out) + MAX(T2out)-MIN(T2out)) \
      FROM kamstrup \
      WHERE (sample_time >= datetime('now', '${interval}')) \
      GROUP BY solhour \
      ;" > "${kamdata}"

  # for debugging
  tail "${kamdata}"
  echo ""

  # convert the data into hourly averages
  # output two separate files for USAGE and PRODUCTION
  ./scripts/kam42.py "${kamdata}" || exit 1

  # for debugging
  tail "${kamdata}u"
  echo ""
  # for debugging
  tail "${kamdata}p"

  if [ "$(wc -l < "${kamdata}")" -gt 5 ]; then
    timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}u'" ./graphs/avgday_u.gp
    timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}p'" ./graphs/avgday_p.gp
  fi

  #./scripts/upload.sh --upload

  # drop datafile
  rm "${kamdata}"
  rm "${kamdata}u"
  rm "${kamdata}p"

popd >/dev/null || exit
