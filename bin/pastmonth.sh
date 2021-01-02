#!/bin/bash

# query daily totals for a period of one month

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)

pushd "${HERE}" >/dev/null || exit 1
    ./trend.py --days 0
    ./upload.sh --upload
popd >/dev/null || exit

CURRENT_EPOCH=$(date +'%s')
# Keep upto 10 years of data
PURGE_EPOCH=$(echo "${CURRENT_EPOCH} - (10 * 366 * 24 * 3600)" | bc)
sqlite3 "${HOME}/.sqlite3/electriciteit.sqlite3" "DELETE FROM kamstrup WHERE sample_epoch < ${PURGE_EPOCH};"
