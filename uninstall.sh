#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)

pushd "${HERE}" || exit 1
    # shellcheck disable=SC1091
    source ./includes

    echo
    echo -n "Started UNinstalling ${app_name} on "
    date
    echo

    # allow user to abort
    sleep 10

    sudo systemctl disable kamstrup.kamstrup.service
    sudo systemctl disable kamstrup.solaredge.service

    sudo systemctl disable kamstrup.backupdb.timer
    sudo systemctl disable kamstrup.trend.day.timer
    sudo systemctl disable kamstrup.trend.month.timer
    sudo systemctl disable kamstrup.trend.year.timer
    sudo systemctl disable kamstrup.update.timer

    ./stop.sh
popd || exit

echo
echo -n "Finished UNinstallation of ${app_name} on "
date
echo "*********************************************************"
echo
