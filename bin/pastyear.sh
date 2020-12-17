#!/bin/bash

# query monthly totals for a period of n years

HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)

pushd "${HERE}" >/dev/null || exit 1
    ./kam44.py --gauge 0 &
    ./kam43.py --months 0 &
    ./kam43.py --years 0 &
    ./kam44.py --months 0 &
    wait
    ./upload.sh --all
popd >/dev/null || exit
