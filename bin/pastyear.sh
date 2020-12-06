#!/bin/bash

# query monthly totals for a period of n years

HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)

pushd "${HERE}" >/dev/null || exit 1
    ./kam43.py -y1
    ./kam43.py -y2
    ./kam44.py -m
    ./kam44.py -g
    ./upload.sh --all
popd >/dev/null || exit
