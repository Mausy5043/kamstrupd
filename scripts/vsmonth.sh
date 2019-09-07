#!/bin/bash

# query monthly totals for a period of n years


interval="-61 month"

pushd "${HOME}/kamstrupd" >/dev/null || exit 1
  #shellcheck disable=SC1091
  source ./scripts/environment.sh
  # totals per hour for T1in, T2in, T1out, T2out

  #shellcheck disable=SC2154
  sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" \
     ".separator '; '" \
     "SELECT strftime('%Y-%m',sample_time) as solmoon, \
             MAX(T1in)-MIN(T1in) + MAX(T2in)-MIN(T2in), \
             MAX(T1out)-MIN(T1out) + MAX(T2out)-MIN(T2out), \
             strftime('%Y',sample_time) as sol, \
             strftime('%m',sample_time) as moon\
      FROM kamstrup \
      WHERE (sample_time >= datetime('now', '${interval}')) \
      GROUP BY solmoon \
      ORDER BY solmoon ASC \
      ;" > "${kamdata}"

  # convert the data into month-rows and year-columns
  ./scripts/kam41.py "${kamdata}"

  if [ "$(wc -l < "${kamdata}")" -gt 5 ]; then
    timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}u'" ./graphs/vsmonth_u.gp
    timeout 120s gnuplot -e "utc_offset='${UTCOFFSET}'; kamdata='${kamdata}p'" ./graphs/vsmonth_p.gp
  fi

  ./scripts/upload.sh --upload

popd >/dev/null || exit

# drop datafiles
rm "${kamdata}"
rm "${kamdata}u"
rm "${kamdata}p"
