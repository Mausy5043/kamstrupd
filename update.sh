#!/bin/bash

# update.sh is run periodically by a service.
# * It synchronises the local copy of ${app_name} with the current GitLab branch
# * It checks the state of and (re-)starts daemons if they are not (yet) running.

logger "Started kamstrup update."

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)

pushd "${HERE}" || exit 1
    # shellcheck disable=SC1091
    source ./bin/constants.sh

    # shellcheck disable=SC2154
    branch=$(<"${HOME}/.${app_name}.branch") || exit 1

    # make sure working tree exists
    if [ ! -d "/tmp/${app_name}/site/img" ]; then
        mkdir -p "/tmp/${app_name}/site/img"
        chmod -R 755 "/tmp/${app_name}"
    fi

    git fetch origin || sleep 60; git fetch origin
    # Check which files have changed
    DIFFLIST=$(git --no-pager diff --name-only "${branch}..origin/${branch}")
    git pull
    git fetch origin
    git checkout "${branch}"
    git reset --hard "origin/${branch}" && git clean -f -d
    chmod -x ./services/*

    sudo systemctl stop kamstrup.fles.service &
    sudo systemctl stop kamstrup.kamstrup.service &
    sudo systemctl stop kamstrup.solaredge.service &
    sudo systemctl stop kamstrup.trend.day.timer &
    sudo systemctl stop kamstrup.trend.month.timer &
    sudo systemctl stop kamstrup.trend.year.timer &
    echo "Please wait while services stop..."; wait

    changed_service=0
    changed_lib=0
    for fname in $DIFFLIST; do
        if [[ "${fname:0:9}" == "services/" ]]; then
            changed_service=1
        fi
        if [[ "${fname:${#fname}-6}" == "lib.py" ]]; then
            changed_lib=1
        fi
    done

    if [[ changed_service -eq 1 ]] || [[ changed_lib -eq 1 ]]; then
        echo "  ! Service or timer changed"
        echo "  o Reinstalling services"
        sudo cp ./services/*.service /etc/systemd/system/
        echo "  o Reinstalling timers"
        sudo cp ./services/*.timer /etc/systemd/system/
        sudo systemctl daemon-reload
    fi

    if [ ! "${1}" == "--systemd" ]; then
        echo "Skipping graph creation"
    else
        echo "Creating graphs [1]"
        bin/pastday.sh
        echo "Creating graphs [2]"
        bin/pastmonth.sh
        echo "Creating graphs [3]"
        bin/pastyear.sh
    fi

    echo "Please wait while services start..."
    sudo systemctl start kamstrup.trend.day.timer
    sudo systemctl start kamstrup.trend.month.timer
    sudo systemctl start kamstrup.trend.year.timer
    sudo systemctl start kamstrup.fles.service &
    sudo systemctl start kamstrup.kamstrup.service &
    sudo systemctl start kamstrup.solaredge.service &
    wait

popd || exit

logger "Finished kamstrup update."
