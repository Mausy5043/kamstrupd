#!/bin/bash

# query hourly totals for a period of two days

HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)

pushd "${HERE}" >/dev/null || exit 1
    ./trend.py --hours 0
    # ./upload.sh --upload
popd >/dev/null || exit
