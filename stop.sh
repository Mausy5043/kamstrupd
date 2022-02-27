#!/bin/bash

# Use stop.sh to stop all daemons in one go
# You can use update.sh to get everything started again.

HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)

pushd "${HERE}" || exit 1
    # shellcheck disable=SC1091
    source ./bin/constants.sh

    sudo systemctl stop kamstrup.fles.service &
    sudo systemctl stop kamstrup.kamstrup.service &
    sudo systemctl stop kamstrup.solaredge.service &

    sudo systemctl stop kamstrup.trend.day.timer &
    sudo systemctl stop kamstrup.trend.month.timer &
    sudo systemctl stop kamstrup.trend.year.timer &
    sudo systemctl stop kamstrup.update.timer &
    wait
popd || exit
