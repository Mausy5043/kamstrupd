#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

# The hostname is in /etc/hostname prior to running `install.sh` here!
HOSTNAME=$(hostname)

echo -n "Started UNinstalling kamstrupd on "; date

# allow user to abort
sleep 10

pushd "${HOME}/kamstrupd" || exit 1
  # shellcheck disable=SC1091
 source ./includes

  # prevent restarts of daemons while the script is still running
  sudo rm /etc/cron.d/kamstrupd

  echo "  Stopping all daemons"
  # shellcheck disable=SC2154
  for daemon in ${runlist}; do
    echo "Stopping kam${daemon}"
    eval "./daemons/kam${daemon}d.py stop"
  done

  ./scripts/kamfile.sh --backup
popd || exit


echo -n "Finished UNinstallation of kamstrupd on "; date
