#!/bin/bash

# update.sh is run periodically by a service.
# * It synchronises the local copy of ${app_name} with the current GitLab branch
# * It checks the state of and (re-)starts daemons if they are not (yet) running.


HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)

pushd "${HERE}" || exit 1
    # shellcheck disable=SC1091
    source ./includes

    # shellcheck disable=SC2154
    branch=$(<"${HOME}/.${app_name}.branch")

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

    changed_config=0
    changed_service=0
    changed_daemon=0
    changed_lib=0
    for fname in $DIFFLIST; do
        if [[ "${fname}" == "config.ini" ]]; then
            changed_config=1
        fi
        if [[ "${fname:0:9}" == "services/" ]]; then
            changed_service=1
        fi
        if [[ "${fname}" == "bin/kamstrup.py" ]]; then
            changed_daemon=1
        fi
        if [[ "${fname}" == "bin/solaredge.py" ]]; then
            changed_daemon=1
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
        sudo systemctl restart kamstrup.kamstrup.service
        sudo systemctl restart kamstrup.solaredge.service
    fi

    if [[ changed_config -eq 1 ]] || [[ changed_daemon -eq 1 ]]; then
        echo "  ! Daemon or configuration changed"
        echo "  o Restarting daemon"
        sudo systemctl restart kamstrup.kamstrup.service
        sudo systemctl restart kamstrup.solaredge.service
    fi

    if [[ "${1}" == "--systemd" ]]; then
        echo "" > /dev/null
    else
        echo "Updating trendgraph..."
        sudo systemctl start kamstrup.trend.day.service
    fi
popd || exit
