#!/bin/bash

# Pull data from MySQL server and graph them.

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
UTCOFFSET=$((LOCALSECONDS - UTCSECONDS))

pushd "$HOME/kamstrupd" >/dev/null
  if [ $(wc -l < /tmp/kamstrupd/mysql/kamd.csv) -gt 5 ]; then
    time gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph11.gp &
    time gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph12.gp &
    time gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph13.gp &
  fi

  wait

popd >/dev/null
