#!/bin/bash

# Use stop.sh to stop all daemons in one go
# You can use update.sh to get everything started kam.

pushd "${HOME}/kamstrupd" || exit 1
  # shellcheck disable=SC1091
  source ./includes

  # Check if DIAG daemons are running
  # shellcheck disable=SC2154
  for daemon in ${kamlist}; do
    # command the daemon to stop regardless if it is running or not.
    eval "./kam${daemon}d.py stop"
    # kill off any rogue daemons by the same name (it happens sometimes)
    if [   "$(pgrep -fc "kam${daemon}d.py")" -ne 0 ]; then
      kill "$(pgrep -f  "kam${daemon}d.py")"
    fi
    # log the activity
    logger -p user.err -t kamstrupd "  * Daemon ${daemon} stopped."
    # force rm the .pid file
    rm -f "/tmp/kamstrupd/${daemon}.pid"
  done

  # Check if SVC daemons are running
  # shellcheck disable=SC2154
  for daemon in ${srvclist}; do
    # command the daemon to stop regardless if it is running or not.
    eval "./kam${daemon}d.py stop"
    # kill off any rogue daemons by the same name (it happens sometimes)
    if [   "$(pgrep -fc "kam${daemon}d.py")" -ne 0 ]; then
      kill "$(pgrep -f  "kam${daemon}d.py")"
    fi
    # log the activity
    logger -p user.err -t kamstrupd "  * Daemon ${daemon} stopped."
    # force rm the .pid file
    rm -f "/tmp/kamstrupd/${daemon}.pid"
  done
popd || exit

echo
echo "To re-start all daemons, use:"
echo "./update.sh"
