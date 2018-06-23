#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

# The hostname is in /etc/hostname prior to running `install.sh` here!
HOSTNAME=$(hostname)

echo -n "Started UNinstalling kamstrupd on "; date

pushd "$HOME/kamstrupd"
 source ./includes

  # prevent restarts of daemons while the script is still running
  sudo rm /etc/cron.d/kamstrupd

  echo "  Stopping all diagnostic daemons"
  for daemon in $kamlist; do
    echo "Stopping ${daemon}"
    eval "./kam${daemon}d.py stop"
  done
  echo "  Stopping all service daemons"
  for daemon in $srvclist; do
    echo "Stopping ${daemon}"
    eval "./kam${daemon}d.py stop"
  done
popd

echo -n "Finished UNinstallation of kamstrupd on "; date
